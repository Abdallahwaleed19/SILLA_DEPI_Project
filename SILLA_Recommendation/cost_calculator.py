"""
SILLA_Recommendation/cost_calculator.py
======================================
Cost calculation module for SILLA recipes and ingredients:
- Grounded strictly in actual prices from silla_staging.db.
- Calculates Pro-rata Consumed Cost (net recipe cost per serving).
- Calculates Grocery Procurement Cost (whole commercial packages).
- Rigorous physical & culinary unit conversions with explicit Exact vs Approximate classification.
- Transparent reporting of unpriced ingredients without guessing or treating as zero.
"""

import sqlite3
import math
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any

from SILLA_Recommendation.config import (
    DB_PATH,
    STANDARD_UNIT_CONVERSIONS,
    PRODUCE_PIECE_WEIGHT_G,
)


class UnitConverter:
    """
    Standardized, documented unit converter grounded in physics and culinary standards.
    Distinguishes strictly between Exact mathematical definitions and Approximate
    culinary/agricultural averages.
    """

    EXACT_VOLUME_UNITS = {
        ("tsp", "ml"): (5.0, "International / Metric Culinary Teaspoon Definition (1 tsp = 5.0 ml)"),
        ("ml", "tsp"): (0.2, "Inverse Metric Teaspoon Definition (1 ml = 0.2 tsp)"),
        ("tbsp", "ml"): (15.0, "International / Metric Culinary Tablespoon Definition (1 tbsp = 15.0 ml)"),
        ("ml", "tbsp"): (1.0 / 15.0, "Inverse Metric Tablespoon Definition (1 ml = 0.0667 tbsp)"),
        ("cup", "ml"): (240.0, "US Legal / Metric Standard Culinary Cup (1 cup = 240.0 ml)"),
        ("ml", "cup"): (1.0 / 240.0, "Inverse Standard Culinary Cup (1 ml = 0.00417 cup)"),
        ("l", "ml"): (1000.0, "SI Metric System Standard (1 L = 1000.0 ml)"),
        ("ml", "l"): (0.001, "SI Metric System Standard (1 ml = 0.001 L)"),
    }

    EXACT_MASS_UNITS = {
        ("g", "g"): (1.0, "SI Metric Identity"),
        ("kg", "g"): (1000.0, "SI Metric System Standard (1 kg = 1000.0 g)"),
        ("g", "kg"): (0.001, "SI Metric System Standard (1 g = 0.001 kg)"),
    }

    @classmethod
    def convert_detailed(
        cls,
        qty: float,
        from_unit: str,
        to_unit: str,
        ingredient_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Convert quantity from source unit to target unit with full audit metadata.
        
        Returns:
            Dictionary containing:
            - converted_quantity: Optional[float]
            - classification: "EXACT" | "APPROXIMATE" | "UNSUPPORTED"
            - method: str
            - source_standard: str
            - estimated_variance_pct: float (0.0 for EXACT)
            - is_supported: bool
        """
        if qty is None or qty <= 0:
            return {
                "converted_quantity": 0.0,
                "classification": "EXACT",
                "method": "zero_quantity",
                "source_standard": "Zero Quantity Definition",
                "estimated_variance_pct": 0.0,
                "is_supported": True,
            }

        from_u = str(from_unit).lower().strip()
        to_u = str(to_unit).lower().strip()

        # 1. Exact identical unit match
        if from_u == to_u:
            return {
                "converted_quantity": float(qty),
                "classification": "EXACT",
                "method": "exact_unit_match",
                "source_standard": "Identity Mapping (Same Unit)",
                "estimated_variance_pct": 0.0,
                "is_supported": True,
            }

        # 2. Exact SI Mass
        if (from_u, to_u) in cls.EXACT_MASS_UNITS:
            factor, std = cls.EXACT_MASS_UNITS[(from_u, to_u)]
            return {
                "converted_quantity": float(qty * factor),
                "classification": "EXACT",
                "method": f"standard_metric_{from_u}_to_{to_u}",
                "source_standard": std,
                "estimated_variance_pct": 0.0,
                "is_supported": True,
            }

        # 3. Exact SI / Standard Volume
        if (from_u, to_u) in cls.EXACT_VOLUME_UNITS:
            factor, std = cls.EXACT_VOLUME_UNITS[(from_u, to_u)]
            return {
                "converted_quantity": float(qty * factor),
                "classification": "EXACT",
                "method": f"standard_volume_{from_u}_to_{to_u}",
                "source_standard": std,
                "estimated_variance_pct": 0.0,
                "is_supported": True,
            }

        # 4. Approximate Volume-to-Mass (Culinary bulk density approximation)
        if (from_u, to_u) in [("tsp", "g"), ("tbsp", "g"), ("cup", "g")]:
            factor = STANDARD_UNIT_CONVERSIONS[(from_u, to_u)]
            return {
                "converted_quantity": float(qty * factor),
                "classification": "APPROXIMATE",
                "method": f"culinary_volume_to_mass_{from_u}_to_{to_u}",
                "source_standard": f"Culinary Bulk Density Approximation (1 {from_u} ≈ {factor}g at rho ≈ 1.0 g/ml)",
                "estimated_variance_pct": 25.0,
                "is_supported": True,
            }

        if (to_u, from_u) in [("tsp", "g"), ("tbsp", "g"), ("cup", "g")]:
            factor = 1.0 / STANDARD_UNIT_CONVERSIONS[(to_u, from_u)]
            return {
                "converted_quantity": float(qty * factor),
                "classification": "APPROXIMATE",
                "method": f"inverse_culinary_mass_to_volume_{from_u}_to_{to_u}",
                "source_standard": f"Inverse Culinary Density Approximation (rho ≈ 1.0 g/ml)",
                "estimated_variance_pct": 25.0,
                "is_supported": True,
            }

        # 5. Approximate Produce Piece-to-Gram (Egyptian Market Average Weights)
        if from_u == "piece" and to_u in ("g", "kg"):
            piece_weight = PRODUCE_PIECE_WEIGHT_G.get(ingredient_id, 100.0)
            total_g = qty * piece_weight
            variance = 10.0 if ingredient_id == "ING0028" else 25.0
            if to_u == "kg":
                return {
                    "converted_quantity": float(total_g / 1000.0),
                    "classification": "APPROXIMATE",
                    "method": f"produce_piece_to_kg_{piece_weight}g",
                    "source_standard": f"Egyptian Supermarket & Agricultural Average Weight (1 piece ≈ {piece_weight}g)",
                    "estimated_variance_pct": variance,
                    "is_supported": True,
                }
            return {
                "converted_quantity": float(total_g),
                "classification": "APPROXIMATE",
                "method": f"produce_piece_to_g_{piece_weight}g",
                "source_standard": f"Egyptian Supermarket & Agricultural Average Weight (1 piece ≈ {piece_weight}g)",
                "estimated_variance_pct": variance,
                "is_supported": True,
            }

        if from_u in ("g", "kg") and to_u == "piece":
            if ingredient_id not in PRODUCE_PIECE_WEIGHT_G:
                return {
                    "converted_quantity": None,
                    "classification": "UNSUPPORTED",
                    "method": f"UNSUPPORTED_CONVERSION_{from_u}_TO_piece_FOR_NON_PRODUCE",
                    "source_standard": "None (Cannot convert mass to pieces without piece weight definition)",
                    "estimated_variance_pct": None,
                    "is_supported": False,
                }
            piece_weight = PRODUCE_PIECE_WEIGHT_G[ingredient_id]
            total_g = qty * 1000.0 if from_u == "kg" else qty
            variance = 10.0 if ingredient_id == "ING0028" else 25.0
            return {
                "converted_quantity": float(total_g / piece_weight),
                "classification": "APPROXIMATE",
                "method": f"produce_g_to_piece_{piece_weight}g",
                "source_standard": f"Egyptian Supermarket & Agricultural Average Weight (1 piece ≈ {piece_weight}g)",
                "estimated_variance_pct": variance,
                "is_supported": True,
            }

        # 6. Approximate Garlic Clove-to-Gram
        if from_u == "clove" and to_u == "g":
            return {
                "converted_quantity": float(qty * 4.0),
                "classification": "APPROXIMATE",
                "method": "culinary_clove_to_g_4g",
                "source_standard": "USDA / International Culinary Standard Average Garlic Clove (3-5g, avg 4.0g)",
                "estimated_variance_pct": 25.0,
                "is_supported": True,
            }
        if from_u == "g" and to_u == "clove":
            return {
                "converted_quantity": float(qty / 4.0),
                "classification": "APPROXIMATE",
                "method": "culinary_g_to_clove_4g",
                "source_standard": "USDA / International Culinary Standard Average Garlic Clove (3-5g, avg 4.0g)",
                "estimated_variance_pct": 25.0,
                "is_supported": True,
            }

        # 7. Approximate Fresh Herb Bunch-to-Gram
        if from_u == "bunch" and to_u == "g":
            return {
                "converted_quantity": float(qty * 50.0),
                "classification": "APPROXIMATE",
                "method": "culinary_bunch_to_g_50g",
                "source_standard": "Egyptian Local Fresh Market Herb Bundle Average (40-70g, avg 50.0g)",
                "estimated_variance_pct": 30.0,
                "is_supported": True,
            }
        if from_u == "g" and to_u == "bunch":
            return {
                "converted_quantity": float(qty / 50.0),
                "classification": "APPROXIMATE",
                "method": "culinary_g_to_bunch_50g",
                "source_standard": "Egyptian Local Fresh Market Herb Bundle Average (40-70g, avg 50.0g)",
                "estimated_variance_pct": 30.0,
                "is_supported": True,
            }

        # 8. Approximate Aqueous Solution Density (rho ≈ 1.00 g/ml)
        if (from_u == "g" and to_u == "ml") or (from_u == "ml" and to_u == "g"):
            return {
                "converted_quantity": float(qty),
                "classification": "APPROXIMATE",
                "method": f"culinary_density_water_approx_{from_u}_to_{to_u}",
                "source_standard": "Aqueous Solution Density Approximation (Water rho=1.00, Milk rho=1.03, Oil rho=0.92)",
                "estimated_variance_pct": 8.0,
                "is_supported": True,
            }

        # 9. Approximate Piece to ML
        if from_u == "piece" and to_u == "ml":
            return {
                "converted_quantity": float(qty * 50.0),
                "classification": "APPROXIMATE",
                "method": "culinary_piece_to_ml_approx_50ml",
                "source_standard": "Egg / Citrus Fruit Average Liquid Volume (avg 50.0 ml)",
                "estimated_variance_pct": 30.0,
                "is_supported": True,
            }

        # 10. Unsupported / Incompatible
        return {
            "converted_quantity": None,
            "classification": "UNSUPPORTED",
            "method": f"UNSUPPORTED_CONVERSION_{from_u}_TO_{to_u}",
            "source_standard": "None (Dimensional Incompatibility or Undefined Unit)",
            "estimated_variance_pct": None,
            "is_supported": False,
        }

    @classmethod
    def convert(
        cls,
        qty: float,
        from_unit: str,
        to_unit: str,
        ingredient_id: Optional[str] = None
    ) -> Tuple[Optional[float], str]:
        """
        Backwards-compatible wrapper returning (converted_quantity, method).
        """
        detailed = cls.convert_detailed(qty, from_unit, to_unit, ingredient_id)
        return detailed["converted_quantity"], detailed["method"]


class CostCalculator:
    """
    Calculates empirical recipe costs and package procurement requirements from SQLite database.
    """

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            raise FileNotFoundError(f"Database not found at {self.db_path}")

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def calculate_recipe_cost(
        self,
        recipe_id: str,
        store_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate complete cost breakdown for a specific recipe.
        
        Args:
            recipe_id: Target recipe ID (e.g. 'R0001').
            store_id: Optional store filter (e.g. 'STR001' for Carrefour).
            
        Returns:
            Dictionary containing recipe details, priced items, unpriced items,
            net consumed cost, grocery procurement cost, per-serving values,
            and completeness ratios.
        """
        with self._get_connection() as conn:
            c = conn.cursor()

            # 1. Fetch recipe metadata
            recipe = c.execute(
                """
                SELECT recipe_id, recipe_name_ar, recipe_name_en, base_servings, cuisine, category
                FROM recipes
                WHERE recipe_id = ?
                """,
                (recipe_id,)
            ).fetchone()

            if not recipe:
                return {
                    "success": False,
                    "error": f"Recipe ID '{recipe_id}' not found in database.",
                    "recipe_id": recipe_id,
                }

            servings = float(recipe["base_servings"]) if recipe["base_servings"] and float(recipe["base_servings"]) > 0 else 4.0

            # 2. Fetch recipe ingredients
            ingredients = c.execute(
                """
                SELECT 
                    ri.recipe_ingredient_id,
                    ri.ingredient_id,
                    ri.original_ingredient_name,
                    ri.quantity,
                    ri.unit,
                    ri.is_optional,
                    i.canonical_name_ar,
                    i.canonical_name_en
                FROM recipe_ingredients ri
                LEFT JOIN ingredients i ON ri.ingredient_id = i.ingredient_id
                WHERE ri.recipe_id = ?
                ORDER BY ri.recipe_ingredient_id
                """,
                (recipe_id,)
            ).fetchall()

            priced_items: List[Dict[str, Any]] = []
            unpriced_items: List[Dict[str, Any]] = []

            total_net_cost = 0.0
            total_procurement_cost = 0.0

            for ing in ingredients:
                ing_id = ing["ingredient_id"]
                req_qty = float(ing["quantity"])
                req_unit = str(ing["unit"]).strip()
                name_ar = ing["canonical_name_ar"] or ing["original_ingredient_name"]
                name_en = ing["canonical_name_en"] or ing["original_ingredient_name"]

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
                        "required_quantity": req_qty,
                        "required_unit": req_unit,
                        "is_optional": bool(ing["is_optional"]),
                        "reason": "NO_MATCHING_PRODUCT_IN_DATABASE" if not store_id else f"NO_PRODUCT_IN_STORE_{store_id}",
                    })
                    continue

                # Select best product (lowest unit price in compatible units)
                best_candidate = None
                best_unit_price = float("inf")
                best_detailed = None

                for p in products:
                    p_unit = p["package_unit"]
                    p_size = float(p["package_size"])
                    p_price = float(p["price_egp"])

                    detailed = UnitConverter.convert_detailed(req_qty, req_unit, p_unit, ing_id)
                    converted_qty = detailed["converted_quantity"]
                    if converted_qty is None:
                        continue

                    # Calculate unit price in currency per package unit
                    unit_price = p_price / p_size
                    if unit_price < best_unit_price:
                        best_unit_price = unit_price
                        best_candidate = p
                        best_detailed = detailed

                if not best_candidate or best_detailed is None:
                    unpriced_items.append({
                        "ingredient_id": ing_id,
                        "ingredient_name_ar": name_ar,
                        "ingredient_name_en": name_en,
                        "required_quantity": req_qty,
                        "required_unit": req_unit,
                        "is_optional": bool(ing["is_optional"]),
                        "reason": f"INCOMPATIBLE_UNIT_CONVERSION_WITH_PRODUCTS ({req_unit})",
                    })
                    continue

                best_converted_qty = best_detailed["converted_quantity"]

                # Calculate item costs
                pkg_size = float(best_candidate["package_size"])
                pkg_unit = best_candidate["package_unit"]
                pkg_price = float(best_candidate["price_egp"])

                # Pro-rata consumed cost
                pro_rata_cost = (best_converted_qty / pkg_size) * pkg_price

                # Whole grocery packages required (always covers needed quantity)
                packages_needed = math.ceil(best_converted_qty / pkg_size)
                if packages_needed <= 0:
                    packages_needed = 1

                procurement_cost = packages_needed * pkg_price
                leftover_quantity = (packages_needed * pkg_size) - best_converted_qty

                total_net_cost += pro_rata_cost
                total_procurement_cost += procurement_cost

                priced_items.append({
                    "ingredient_id": ing_id,
                    "ingredient_name_ar": name_ar,
                    "ingredient_name_en": name_en,
                    "required_quantity": req_qty,
                    "required_unit": req_unit,
                    "converted_quantity": round(best_converted_qty, 3),
                    "converted_unit": pkg_unit,
                    "conversion_classification": best_detailed["classification"],
                    "conversion_method": best_detailed["method"],
                    "source_standard": best_detailed["source_standard"],
                    "estimated_variance_pct": best_detailed["estimated_variance_pct"],
                    "matched_product": {
                        "product_id": best_candidate["product_id"],
                        "product_name": best_candidate["product_name"],
                        "product_name_ar": best_candidate["product_name_ar"],
                        "brand": best_candidate["brand"],
                        "store_id": best_candidate["store_id"],
                        "package_size": pkg_size,
                        "package_unit": pkg_unit,
                        "price_egp": pkg_price,
                    },
                    "packages_needed": packages_needed,
                    "pro_rata_cost_egp": round(pro_rata_cost, 2),
                    "procurement_cost_egp": round(procurement_cost, 2),
                    "leftover_quantity": round(leftover_quantity, 3),
                    "leftover_unit": pkg_unit,
                })

            total_count = len(ingredients)
            priced_count = len(priced_items)
            unpriced_count = len(unpriced_items)
            completeness_ratio = priced_count / total_count if total_count > 0 else 0.0
            is_fully_priced = (unpriced_count == 0)

            # Disclaimer for transparency
            if is_fully_priced:
                disclaimer = "جميع مكونات الوصفة مسعرة بنسبة 100% بناءً على المنتجات المتاحة في قاعدة البيانات."
            else:
                disclaimer = (
                    f"تنبيه: التكلفة المعروضة تغطي {priced_count} من أصل {total_count} مكونًا "
                    f"({completeness_ratio * 100:.1f}%). يوجد {unpriced_count} مكونًا بدون منتجات مطابقة "
                    f"في قاعدة البيانات، ولم تُحسب تكلفتها بصفر، بل تم إدراجها بشكل مستقل لضمان الشفافية."
                )

            return {
                "success": True,
                "recipe_id": recipe["recipe_id"],
                "recipe_name_ar": recipe["recipe_name_ar"],
                "recipe_name_en": recipe["recipe_name_en"],
                "cuisine": recipe["cuisine"],
                "category": recipe["category"],
                "base_servings": servings,
                "store_id_filter": store_id,
                # Cost Metrics
                "net_recipe_cost_egp": round(total_net_cost, 2),
                "net_cost_per_serving_egp": round(total_net_cost / servings, 2),
                "grocery_procurement_cost_egp": round(total_procurement_cost, 2),
                "procurement_cost_per_serving_egp": round(total_procurement_cost / servings, 2),
                # Completeness & Availability
                "total_ingredients_count": total_count,
                "priced_ingredients_count": priced_count,
                "unpriced_ingredients_count": unpriced_count,
                "price_completeness_ratio": round(completeness_ratio, 4),
                "is_fully_priced": is_fully_priced,
                "pricing_disclaimer": disclaimer,
                # Line Items
                "priced_ingredients": priced_items,
                "unpriced_ingredients": unpriced_items,
            }

    def calculate_multiple_recipes_cost(
        self,
        recipe_ids: List[str],
        store_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate individual costs for multiple recipes.
        """
        results = {}
        for rid in recipe_ids:
            results[rid] = self.calculate_recipe_cost(rid, store_id=store_id)
        return results
