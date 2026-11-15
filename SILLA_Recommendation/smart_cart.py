"""
SILLA_Recommendation/smart_cart.py
==================================
Smart Cart multi-recipe optimizer for SILLA:
- Aggregates shared ingredients across multiple selected recipes.
- Unifies quantities into standardized units.
- Eliminates duplicate package purchases in the supermarket.
- Computes exact comparative savings between separate carts and Smart Cart.
- Explicitly tracks unpriced ingredients that cannot be fulfilled from database.
"""

import sqlite3
import math
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Optional, Any

from SILLA_Recommendation.config import DB_PATH
from SILLA_Recommendation.cost_calculator import UnitConverter, CostCalculator


class SmartCart:
    """
    Optimizes multi-recipe grocery shopping by consolidating common ingredients
    to prevent redundant package purchases.
    """

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found at {self.db_path}")
        self.cost_calculator = CostCalculator(self.db_path)

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def build_smart_cart(
        self,
        recipe_ids: List[str],
        store_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Build an optimized grocery shopping cart for a list of recipes.
        
        Args:
            recipe_ids: List of recipe IDs (e.g. ['R0001', 'R0007']).
            store_id: Optional supermarket ID filter (e.g. 'STR001').
            
        Returns:
            Dictionary containing cart items, savings analysis, itemized comparisons,
            and unpriced ingredients audit.
        """
        if not recipe_ids:
            return {
                "success": False,
                "error": "No recipe IDs provided.",
                "total_cost_egp": 0.0,
                "total_savings_egp": 0.0,
                "cart_items": [],
            }

        # Deduplicate recipe_ids preserving order
        unique_recipe_ids = list(dict.fromkeys(recipe_ids))

        with self._get_connection() as conn:
            c = conn.cursor()

            # 1. Fetch recipe metadata
            placeholders = ",".join("?" for _ in unique_recipe_ids)
            recipes_data = c.execute(
                f"""
                SELECT recipe_id, recipe_name_ar, recipe_name_en, base_servings, cuisine, category
                FROM recipes
                WHERE recipe_id IN ({placeholders})
                """,
                unique_recipe_ids
            ).fetchall()

            recipe_meta_map = {r["recipe_id"]: dict(r) for r in recipes_data}

            # Check for missing recipe IDs
            found_ids = set(recipe_meta_map.keys())
            missing_ids = [rid for rid in unique_recipe_ids if rid not in found_ids]
            if missing_ids:
                return {
                    "success": False,
                    "error": f"One or more recipes not found: {missing_ids}",
                    "missing_recipe_ids": missing_ids,
                }

            # 2. Fetch individual recipe costs for baseline comparison
            individual_costs = {}
            total_separate_procurement_cost = 0.0
            total_net_consumed_cost = 0.0

            for rid in unique_recipe_ids:
                rcost = self.cost_calculator.calculate_recipe_cost(rid, store_id=store_id)
                individual_costs[rid] = rcost
                if rcost.get("success", False):
                    total_separate_procurement_cost += rcost.get("grocery_procurement_cost_egp", 0.0)
                    total_net_consumed_cost += rcost.get("net_recipe_cost_egp", 0.0)

            # 3. Query all ingredient rows across chosen recipes
            ing_rows = c.execute(
                f"""
                SELECT 
                    ri.recipe_id,
                    ri.ingredient_id,
                    ri.original_ingredient_name,
                    ri.quantity,
                    ri.unit,
                    ri.is_optional,
                    i.canonical_name_ar,
                    i.canonical_name_en,
                    r.recipe_name_ar
                FROM recipe_ingredients ri
                JOIN ingredients i ON ri.ingredient_id = i.ingredient_id
                JOIN recipes r ON ri.recipe_id = r.recipe_id
                WHERE ri.recipe_id IN ({placeholders})
                ORDER BY ri.ingredient_id, ri.recipe_id
                """,
                unique_recipe_ids
            ).fetchall()

            # Group ingredient requirements by canonical ingredient_id
            grouped_ingredients = defaultdict(list)
            for row in ing_rows:
                grouped_ingredients[row["ingredient_id"]].append({
                    "recipe_id": row["recipe_id"],
                    "recipe_name_ar": row["recipe_name_ar"],
                    "original_name": row["original_ingredient_name"],
                    "quantity": float(row["quantity"]),
                    "unit": str(row["unit"]).strip(),
                    "is_optional": bool(row["is_optional"]),
                    "canonical_name_ar": row["canonical_name_ar"] or row["original_ingredient_name"],
                    "canonical_name_en": row["canonical_name_en"] or row["original_ingredient_name"],
                })

            cart_items: List[Dict[str, Any]] = []
            unpriced_items: List[Dict[str, Any]] = []
            total_smart_procurement_cost = 0.0
            total_shared_savings = 0.0

            # 4. Consolidate and select optimal packaging
            for ing_id, usages in grouped_ingredients.items():
                name_ar = usages[0]["canonical_name_ar"]
                name_en = usages[0]["canonical_name_en"]

                # Fetch available in-stock products
                prod_query = """
                    SELECT 
                        product_id,
                        product_name,
                        product_name_ar,
                        brand,
                        package_size,
                        package_unit,
                        price_egp,
                        store_id
                    FROM products
                    WHERE ingredient_id = ? AND availability = 'in_stock'
                """
                params: List[Any] = [ing_id]
                if store_id:
                    prod_query += " AND store_id = ?"
                    params.append(store_id)

                products = c.execute(prod_query, params).fetchall()

                if not products:
                    unpriced_items.append({
                        "ingredient_id": ing_id,
                        "ingredient_name_ar": name_ar,
                        "ingredient_name_en": name_en,
                        "used_in_recipes": list({u["recipe_name_ar"] for u in usages}),
                        "recipe_count": len(usages),
                        "usages": [
                            {
                                "recipe_id": u["recipe_id"],
                                "recipe_name_ar": u["recipe_name_ar"],
                                "quantity": u["quantity"],
                                "unit": u["unit"],
                            }
                            for u in usages
                        ],
                        "reason": "NO_MATCHING_PRODUCT_IN_DATABASE" if not store_id else f"NO_PRODUCT_IN_STORE_{store_id}",
                    })
                    continue

                # Find best product (lowest unit price)
                best_product = None
                best_unit_price = float("inf")

                for p in products:
                    p_size = float(p["package_size"])
                    p_price = float(p["price_egp"])
                    unit_price = p_price / p_size
                    if unit_price < best_unit_price:
                        best_unit_price = unit_price
                        best_product = p

                pkg_id = best_product["product_id"]
                pkg_name = best_product["product_name"]
                pkg_name_ar = best_product["product_name_ar"]
                pkg_brand = best_product["brand"]
                pkg_store = best_product["store_id"]
                pkg_size = float(best_product["package_size"])
                pkg_unit = best_product["package_unit"]
                pkg_price = float(best_product["price_egp"])

                # Convert all recipe usages to the product package unit
                total_qty_needed = 0.0
                separate_pkgs_sum = 0
                item_recipe_breakdown = []

                for u in usages:
                    detailed = UnitConverter.convert_detailed(u["quantity"], u["unit"], pkg_unit, ing_id)
                    converted_qty = detailed["converted_quantity"]
                    if converted_qty is None:
                        converted_qty = u["quantity"]

                    total_qty_needed += converted_qty
                    sep_pkgs = math.ceil(converted_qty / pkg_size)
                    if sep_pkgs <= 0:
                        sep_pkgs = 1
                    separate_pkgs_sum += sep_pkgs

                    item_recipe_breakdown.append({
                        "recipe_id": u["recipe_id"],
                        "recipe_name_ar": u["recipe_name_ar"],
                        "original_quantity": u["quantity"],
                        "original_unit": u["unit"],
                        "converted_quantity": round(converted_qty, 3),
                        "converted_unit": pkg_unit,
                        "conversion_classification": detailed["classification"],
                        "conversion_method": detailed["method"],
                        "separate_packages_needed": sep_pkgs,
                    })

                # Calculate smart consolidated packages
                smart_packages_needed = math.ceil(total_qty_needed / pkg_size)
                if smart_packages_needed <= 0:
                    smart_packages_needed = 1

                smart_cost = round(smart_packages_needed * pkg_price, 2)
                separate_cost = round(separate_pkgs_sum * pkg_price, 2)
                savings = round(separate_cost - smart_cost, 2)
                if savings < 0:
                    savings = 0.0

                total_smart_procurement_cost += smart_cost
                total_shared_savings += savings

                is_shared = len(usages) > 1
                leftover_quantity = (smart_packages_needed * pkg_size) - total_qty_needed

                cart_items.append({
                    "ingredient_id": ing_id,
                    "ingredient_name_ar": name_ar,
                    "ingredient_name_en": name_en,
                    "is_shared": is_shared,
                    "shared_recipe_count": len(usages),
                    "total_quantity_needed": round(total_qty_needed, 3),
                    "unit": pkg_unit,
                    "product": {
                        "product_id": pkg_id,
                        "product_name": pkg_name,
                        "product_name_ar": pkg_name_ar,
                        "brand": pkg_brand,
                        "store_id": pkg_store,
                        "package_size": pkg_size,
                        "package_unit": pkg_unit,
                        "price_egp": pkg_price,
                        "unit_price_egp": round(pkg_price / pkg_size, 4),
                    },
                    "smart_packages_needed": smart_packages_needed,
                    "smart_cost_egp": smart_cost,
                    "separate_packages_needed": separate_pkgs_sum,
                    "separate_cost_egp": separate_cost,
                    "savings_egp": savings,
                    "leftover_quantity": round(leftover_quantity, 3),
                    "recipe_breakdown": item_recipe_breakdown,
                })

            # Sort cart items: shared ingredients first (highest savings first), then non-shared
            cart_items.sort(
                key=lambda x: (x["is_shared"], x["savings_egp"], x["smart_cost_egp"]),
                reverse=True
            )

            total_smart_procurement_cost = round(total_smart_procurement_cost, 2)
            total_separate_procurement_cost = round(total_separate_procurement_cost, 2)
            total_shared_savings = round(total_shared_savings, 2)
            savings_pct = round((total_shared_savings / total_separate_procurement_cost) * 100.0, 2) if total_separate_procurement_cost > 0 else 0.0

            shared_count = sum(1 for item in cart_items if item["is_shared"])
            single_count = len(cart_items) - shared_count

            # Build shopping advice message
            if shared_count > 0:
                summary_msg = (
                    f"تم تجميع السلة الذكية لـ {len(unique_recipe_ids)} وصفات بنجاح. "
                    f"تم توفير {total_shared_savings:.2f} ج.م ({savings_pct:.1f}%) "
                    f"من خلال دمج {shared_count} مكونات مشتركة ومنع تكرار شراء العبوات."
                )
            else:
                summary_msg = (
                    f"تم تجميع السلة لـ {len(unique_recipe_ids)} وصفات بنجاح. "
                    f"لا توجد مكونات مشتركة بين الوصفات المختارة."
                )

            return {
                "success": True,
                "recipe_ids": unique_recipe_ids,
                "recipes": [
                    {
                        "recipe_id": r["recipe_id"],
                        "recipe_name_ar": r["recipe_name_ar"],
                        "recipe_name_en": r["recipe_name_en"],
                        "base_servings": r["base_servings"],
                        "cuisine": r["cuisine"],
                        "category": r["category"],
                        "separate_cost_egp": individual_costs[r["recipe_id"]].get("grocery_procurement_cost_egp", 0.0),
                    }
                    for r in recipes_data
                ],
                "store_id_filter": store_id,
                # Financial Totals
                "smart_cart_total_egp": total_smart_procurement_cost,
                "separate_carts_total_egp": total_separate_procurement_cost,
                "total_savings_egp": total_shared_savings,
                "savings_percentage": savings_pct,
                "net_consumed_total_egp": round(total_net_consumed_cost, 2),
                # Aggregation Metrics
                "total_cart_items_count": len(cart_items),
                "shared_ingredients_count": shared_count,
                "unique_ingredients_count": single_count,
                "unpriced_ingredients_count": len(unpriced_items),
                "is_fully_priced": (len(unpriced_items) == 0),
                "summary_message": summary_msg,
                # Details
                "cart_items": cart_items,
                "unpriced_ingredients": unpriced_items,
            }
