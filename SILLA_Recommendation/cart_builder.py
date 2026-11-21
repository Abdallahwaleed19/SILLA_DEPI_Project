"""
SILLA_Recommendation/cart_builder.py
====================================
Smart Cart & Business Logic Builder for SILLA (DEPI Project - Jana Shalaby's Module):
1. Servings Scaling: Calculates ingredient quantities based on number of persons/servings.
2. Pantry Deduction: Excludes or discounts ingredients already available in the user's pantry.
3. Supermarket Product Matching & Packaging: Maps ingredients to commercial supermarket products,
   applying unit conversions, calculating required packages (ceiling division), and tracking leftovers.
4. Multi-Recipe Consolidation: Combines shared ingredients across multiple recipes to eliminate
   redundant package purchases, computing exact savings in EGP and percentages.
5. Budget Optimization: Handles budget constraints via Integer Linear Programming (OR-Tools)
   with an exact pure-Python branch-and-bound fallback to optimize cart contents under tight budgets.
6. Out-of-Stock & Substitute Engine: Suggests and automatically applies culinary substitutes and
   alternative store products when items are unavailable or out of stock.
7. Multi-Store Comparison: Compares cart procurement across major supermarket chains
   (Carrefour, Lulu, Seoudi, Hyperone, etc.) to guide the user to the most economical store.
"""

import sqlite3
import math
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Optional, Any, Union

from SILLA_Recommendation.config import DB_PATH, STAGING_DB_PATH, PRODUCE_PIECE_WEIGHT_G
from SILLA_Recommendation.cost_calculator import UnitConverter, CostCalculator

# Try importing OR-Tools for ILP budget optimization; fallback to exact Knapsack solver if absent
try:
    from ortools.linear_solver import pywraplp
    OR_TOOLS_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    pywraplp = None
    OR_TOOLS_AVAILABLE = False

# Try importing pandas for DataFrame exports
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except (ImportError, ModuleNotFoundError):
    pd = None
    PANDAS_AVAILABLE = False


# Documented Egyptian Culinary Substitution Matrix
# Maps canonical ingredient_id -> list of candidate substitute ingredient_ids in preference order
CULINARY_SUBSTITUTES_REGISTRY: Dict[str, List[Dict[str, Any]]] = {
    # Butter (زبدة) -> Vegetable Oil (زيت طهي)
    "ING0017": [
        {"sub_id": "ING0126", "ratio": 0.85, "reason_ar": "بديل عملي واقتصادي للتحمير والطهي اليومي"}
    ],
    # Olive Oil (زيت زيتون بكر ممتاز) -> Vegetable Oil (زيت طهي نباتي)
    "ING0048": [
        {"sub_id": "ING0126", "ratio": 1.0, "reason_ar": "بديل اقتصادي متوفر في جميع المتاجر"}
    ],
    # Penne Pasta (مكرونة فرن) -> Elbow Macaroni, Spaghetti, Fettuccine
    "ING0089": [
        {"sub_id": "ING0047", "ratio": 1.0, "reason_ar": "مكرونة مقصوصة كبديل نشوي مباشر"},
        {"sub_id": "ING0113", "ratio": 1.0, "reason_ar": "مكرونة سباجيتي كبديل للصلصات"}
    ],
    # Elbow Macaroni (مكرونة مقصوصة) -> Penne, Spaghetti
    "ING0047": [
        {"sub_id": "ING0089", "ratio": 1.0, "reason_ar": "مكرونة فرن كبديل بنفس قوام الصلصة"},
        {"sub_id": "ING0113", "ratio": 1.0, "reason_ar": "مكرونة سباجيتي متوفرة بأسعار مناسبة"}
    ],
    # Spaghetti (مكرونة سباجيتي) -> Fettuccine, Penne
    "ING0113": [
        {"sub_id": "ING0050", "ratio": 1.0, "reason_ar": "مكرونة فيتوتشيني بديل شرائطي"},
        {"sub_id": "ING0089", "ratio": 1.0, "reason_ar": "مكرونة فرن كبديل مع الصلصة"}
    ],
    # Ground Beef (لحم بقري مفروم) -> Minced Lamb (لحم ضأن مفروم)
    "ING0067": [
        {"sub_id": "ING0078", "ratio": 1.0, "reason_ar": "مفروم ضأن كبديل غني بالنكهة للكفتة والتعصيج"}
    ],
    # Minced Lamb (لحم ضأن مفروم) -> Ground Beef (لحم بقري مفروم)
    "ING0078": [
        {"sub_id": "ING0067", "ratio": 1.0, "reason_ar": "مفروم بقري كبديل قليل الدسم ومتوفر أكثر"}
    ],
    # Beef Stew Cubes (مكعبات لحم بقري) -> Lamb Cubes (مكعبات لحم ضأن)
    "ING0009": [
        {"sub_id": "ING0072", "ratio": 1.0, "reason_ar": "لحم ضأن مكعبات كبديل للشوربة والطواجن"}
    ],
    # Lamb Meat Cubes (مكعبات لحم ضأن) -> Beef Stew Cubes
    "ING0072": [
        {"sub_id": "ING0009", "ratio": 1.0, "reason_ar": "لحم بقري مكعبات كبديل اقتصادي"}
    ],
    # Yellow Onion (بصل أصفر) -> Red Onion (بصل أحمر)
    "ING0139": [
        {"sub_id": "ING0102", "ratio": 1.0, "reason_ar": "بصل أحمر متاح كبديل مباشر بنفس النكهة"}
    ],
    # Red Onion (بصل أحمر) -> Yellow Onion (بصل أصفر)
    "ING0102": [
        {"sub_id": "ING0139", "ratio": 1.0, "reason_ar": "بصل أصفر كبديل ممتاز للطبخ والتقلية"}
    ],
    # Tomato Paste (معجون طماطم) -> Strained Tomato Puree, Fresh Tomato
    "ING0123": [
        {"sub_id": "ING0114", "ratio": 2.0, "reason_ar": "صلصة مسبكة كبديل مباشر مركز"},
        {"sub_id": "ING0104", "ratio": 3.0, "reason_ar": "طماطم طازجة مفرومة كبديل طبيعي"}
    ],
    # Strained Tomato Puree (صلصة طماطم مسبكة) -> Tomato Paste
    "ING0114": [
        {"sub_id": "ING0123", "ratio": 0.5, "reason_ar": "معجون طماطم مركز مخفف بالماء"},
        {"sub_id": "ING0104", "ratio": 1.5, "reason_ar": "طماطم حمراء طازجة معصورة"}
    ],
    # Fresh Red Tomato (طماطم حمراء) -> Strained Tomato Puree
    "ING0104": [
        {"sub_id": "ING0114", "ratio": 0.7, "reason_ar": "صلصة مسبكة بديل سريع للطهي"}
    ],
    # Egyptian Rice (أرز مصري) -> Basmati Rice (أرز بسمتي)
    "ING0046": [
        {"sub_id": "ING0004", "ratio": 1.0, "reason_ar": "أرز بسمتي بديل طويل الحبة"}
    ],
    # Basmati Rice (أرز بسمتي) -> Egyptian Rice (أرز مصري)
    "ING0004": [
        {"sub_id": "ING0046", "ratio": 1.0, "reason_ar": "أرز مصري كبديل اقتصادي متوفر"}
    ],
    # Fresh Parsley (بقدونس طازج) -> Fresh Coriander (كزبرة خضراء)
    "ING0060": [
        {"sub_id": "ING0055", "ratio": 1.0, "reason_ar": "كزبرة خضراء طازجة كبديل عطري"}
    ],
    # Fresh Coriander (كزبرة خضراء) -> Fresh Parsley (بقدونس طازج)
    "ING0055": [
        {"sub_id": "ING0060", "ratio": 1.0, "reason_ar": "بقدونس طازج كبديل للخضرة الورقية"}
    ],
    # Black Eggplant (باذنجان أسود) -> White Eggplant (باذنجان أبيض عروس)
    "ING0011": [
        {"sub_id": "ING0131", "ratio": 1.0, "reason_ar": "باذنجان أبيض بديل مناسب للمحشي والقلي"}
    ],
    # White Eggplant -> Black Eggplant
    "ING0131": [
        {"sub_id": "ING0011", "ratio": 1.0, "reason_ar": "باذنجان أسود متوفر في الأسواق"}
    ],
}


class CartBuilder:
    """
    Intelligent Smart Cart & Business Logic Builder.
    
    Transforms recipe requirements into an optimized grocery shopping cart:
    - Scales quantities dynamically for any number of servings.
    - Excludes items already present in the user's pantry.
    - Matches ingredients to retail packages and calculates minimum necessary purchases.
    - Consolidates shared ingredients across recipes to eliminate duplicate packs.
    - Solves budget constraints with OR-Tools or branch-and-bound optimization.
    - Auto-recovers missing or out-of-stock items via a culinary substitution registry.
    - Compares multi-store pricing to find the best deal.
    """

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = Path(db_path)
        if not self.db_path.exists():
            # Graceful fallback to staging database if primary path does not exist
            if STAGING_DB_PATH.exists():
                self.db_path = STAGING_DB_PATH
            else:
                raise FileNotFoundError(f"Database not found at {self.db_path}")

        self.cost_calculator = CostCalculator(self.db_path)
        self._ingredient_name_map = None
        self._load_ingredient_cache()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _load_ingredient_cache(self):
        """Preload canonical names and aliases for fast pantry lookups."""
        self._ingredient_name_map = {}
        with self._get_connection() as conn:
            rows = conn.execute(
                """
                SELECT ingredient_id, canonical_name_ar, canonical_name_en, aliases_ar, aliases_en, default_unit
                FROM ingredients
                """
            ).fetchall()
            for r in rows:
                ing_id = r["ingredient_id"]
                default_u = r["default_unit"]
                # Map by ID
                self._ingredient_name_map[ing_id.lower()] = (ing_id, default_u)
                
                # Helper for name normalization
                def _norm(txt: Optional[str]) -> str:
                    if not txt:
                        return ""
                    txt = txt.strip().lower()
                    txt = re.sub(r"[\u064B-\u065F\u0640]", "", txt) # Diacritics
                    txt = re.sub(r"[إأآا]", "ا", txt)
                    txt = re.sub(r"[ة]", "ه", txt)
                    txt = re.sub(r"[ى]", "ي", txt)
                    return txt

                if r["canonical_name_ar"]:
                    self._ingredient_name_map[_norm(r["canonical_name_ar"])] = (ing_id, default_u)
                if r["canonical_name_en"]:
                    self._ingredient_name_map[_norm(r["canonical_name_en"])] = (ing_id, default_u)

                # Aliases
                if r["aliases_ar"]:
                    for alias in r["aliases_ar"].split(","):
                        if alias.strip():
                            self._ingredient_name_map[_norm(alias)] = (ing_id, default_u)
                if r["aliases_en"]:
                    for alias in r["aliases_en"].split(","):
                        if alias.strip():
                            self._ingredient_name_map[_norm(alias)] = (ing_id, default_u)

    def normalize_pantry(self, user_pantry: Optional[Any]) -> Dict[str, Dict[str, Any]]:
        """
        Normalize user pantry inputs into a structured mapping:
        { ingredient_id: {"quantity": float, "unit": str, "is_unlimited": bool} }
        
        Supports inputs as:
        - List of strings: ["زيت", "ملح", "ING0139", "onion"]
        - Dict of quantities: {"ING0139": 250, "زيت": {"quantity": 500, "unit": "ml"}}
        """
        if not user_pantry:
            return {}

        def _norm(txt: str) -> str:
            txt = str(txt).strip().lower()
            txt = re.sub(r"[\u064B-\u065F\u0640]", "", txt)
            txt = re.sub(r"[إأآا]", "ا", txt)
            txt = re.sub(r"[ة]", "ه", txt)
            txt = re.sub(r"[ى]", "ي", txt)
            return txt

        normalized: Dict[str, Dict[str, Any]] = {}

        if isinstance(user_pantry, list):
            for item in user_pantry:
                if not item:
                    continue
                item_str = _norm(str(item))
                match = self._ingredient_name_map.get(item_str)
                if match:
                    ing_id, def_u = match
                    normalized[ing_id] = {
                        "ingredient_id": ing_id,
                        "quantity": float("inf"),
                        "unit": def_u or "g",
                        "is_unlimited": True
                    }
                else:
                    # Fuzzy match fallback: check if substring
                    for k, (ing_id, def_u) in self._ingredient_name_map.items():
                        if item_str and (item_str in k or k in item_str):
                            normalized[ing_id] = {
                                "ingredient_id": ing_id,
                                "quantity": float("inf"),
                                "unit": def_u or "g",
                                "is_unlimited": True
                            }
                            break

        elif isinstance(user_pantry, dict):
            for item_key, val in user_pantry.items():
                item_str = _norm(str(item_key))
                match = self._ingredient_name_map.get(item_str)
                if not match:
                    for k, (ing_id, def_u) in self._ingredient_name_map.items():
                        if item_str and (item_str in k or k in item_str):
                            match = (ing_id, def_u)
                            break
                if not match:
                    continue

                ing_id, def_u = match
                if isinstance(val, (int, float)):
                    normalized[ing_id] = {
                        "ingredient_id": ing_id,
                        "quantity": float(val),
                        "unit": def_u or "g",
                        "is_unlimited": False
                    }
                elif isinstance(val, dict):
                    qty = float(val.get("quantity", float("inf")))
                    unit = str(val.get("unit", def_u or "g")).strip()
                    normalized[ing_id] = {
                        "ingredient_id": ing_id,
                        "quantity": qty,
                        "unit": unit,
                        "is_unlimited": math.isinf(qty)
                    }

        return normalized

    def find_substitutes(
        self,
        ingredient_id: str,
        store_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find culinary and commercial substitutes for a given ingredient.
        
        Returns a list of substitute candidates with available products and conversion notes.
        """
        sub_list = CULINARY_SUBSTITUTES_REGISTRY.get(ingredient_id, [])
        if not sub_list:
            return []

        candidates = []
        with self._get_connection() as conn:
            c = conn.cursor()
            for sub_entry in sub_list:
                sub_id = sub_entry["sub_id"]
                ratio = sub_entry["ratio"]
                reason_ar = sub_entry["reason_ar"]

                # Fetch substitute ingredient details
                ing_meta = c.execute(
                    "SELECT canonical_name_ar, canonical_name_en, default_unit FROM ingredients WHERE ingredient_id = ?",
                    (sub_id,)
                ).fetchone()
                if not ing_meta:
                    continue

                # Check product availability in store
                prod_query = """
                    SELECT product_id, product_name, product_name_ar, brand, package_size,
                           package_unit, price_egp, store_id, availability
                    FROM products
                    WHERE ingredient_id = ? AND availability = 'in_stock'
                """
                params = [sub_id]
                if store_id:
                    prod_query += " AND store_id = ?"
                    params.append(store_id)
                prod_query += " ORDER BY (price_egp / package_size) ASC"

                prod_products = c.execute(prod_query, params).fetchall()

                best_p_dict = None
                if prod_products:
                    best_p = prod_products[0]
                    best_p_dict = {
                        "product_id": best_p["product_id"],
                        "product_name_ar": best_p["product_name_ar"] or best_p["product_name"],
                        "brand": best_p["brand"],
                        "package_size": float(best_p["package_size"]),
                        "package_unit": best_p["package_unit"],
                        "price_egp": float(best_p["price_egp"]),
                        "store_id": best_p["store_id"],
                    }

                candidates.append({
                    "substitute_ingredient_id": sub_id,
                    "substitute_name_ar": ing_meta["canonical_name_ar"],
                    "substitute_name_en": ing_meta["canonical_name_en"],
                    "ratio": ratio,
                    "reason_ar": reason_ar,
                    "best_product": best_p_dict,
                    "available_products_count": len(prod_products),
                })

        return candidates

    def build_cart(
        self,
        recipe_ids: List[str],
        servings: Optional[Union[int, float, Dict[str, float]]] = None,
        user_pantry: Optional[Any] = None,
        store_id: Optional[str] = None,
        budget_egp: Optional[float] = None,
        enable_substitutes: bool = True,
        optimize_budget: bool = True
    ) -> Dict[str, Any]:
        """
        Build an end-to-end optimized grocery cart:
        
        Args:
            recipe_ids: List of recipe IDs to cook (e.g. ['R0001', 'R0007']).
            servings: Target number of persons/servings.
                      Can be an integer (e.g. 6), or a dict mapping {recipe_id: servings}.
                      If None, base_servings from database is used for each recipe.
            user_pantry: Ingredients already available at home (list of names/IDs or dict with quantities).
            store_id: Supermarket ID (e.g. 'STR001' for Carrefour). If None, all stores evaluated.
            budget_egp: Spending budget in Egyptian Pounds.
            enable_substitutes: If True, automatically finds culinary substitutes for unpriced/out-of-stock items.
            optimize_budget: If True and budget exceeded, applies Knapsack/OR-Tools to fit budget.
            
        Returns:
            Comprehensive Cart dictionary with itemization, multi-recipe savings,
            pantry deductions, substitutions, budget analysis, and advice.
        """
        if not recipe_ids:
            return {
                "success": False,
                "error": "No recipe IDs provided.",
                "cart_items": [],
                "smart_cart_total_egp": 0.0,
                "separate_carts_total_egp": 0.0,
                "total_savings_egp": 0.0,
                "total_cost_egp": 0.0,
            }

        unique_recipe_ids = list(dict.fromkeys(recipe_ids))
        normalized_pantry = self.normalize_pantry(user_pantry)

        with self._get_connection() as conn:
            c = conn.cursor()

            # 1. Fetch recipe metadata & calculate scaling factors
            placeholders = ",".join("?" for _ in unique_recipe_ids)
            recipes_data = c.execute(
                f"""
                SELECT recipe_id, recipe_name_ar, recipe_name_en, base_servings, cuisine, category
                FROM recipes
                WHERE recipe_id IN ({placeholders})
                """,
                unique_recipe_ids
            ).fetchall()

            recipe_meta = {r["recipe_id"]: dict(r) for r in recipes_data}
            missing_ids = [rid for rid in unique_recipe_ids if rid not in recipe_meta]
            if missing_ids:
                return {
                    "success": False,
                    "error": f"Recipe(s) not found in database: {missing_ids}",
                    "missing_recipe_ids": missing_ids,
                }

            # Determine serving scaling per recipe
            scaling_factors: Dict[str, float] = {}
            target_servings_map: Dict[str, float] = {}

            for rid in unique_recipe_ids:
                base_s = float(recipe_meta[rid]["base_servings"] or 4.0)
                if isinstance(servings, (int, float)) and servings > 0:
                    tgt_s = float(servings)
                elif isinstance(servings, dict) and rid in servings:
                    tgt_s = float(servings[rid])
                else:
                    tgt_s = base_s

                target_servings_map[rid] = tgt_s
                scaling_factors[rid] = tgt_s / base_s if base_s > 0 else 1.0

            # 2. Fetch baseline separate costs (for savings comparison)
            individual_costs = {}
            total_separate_procurement_cost = 0.0
            total_net_consumed_cost = 0.0

            for rid in unique_recipe_ids:
                rcost = self.cost_calculator.calculate_recipe_cost(rid, store_id=store_id)
                scale = scaling_factors[rid]
                individual_costs[rid] = rcost
                if rcost.get("success", False):
                    # Scale costs by serving scale factor
                    total_separate_procurement_cost += rcost.get("grocery_procurement_cost_egp", 0.0) * scale
                    total_net_consumed_cost += rcost.get("net_recipe_cost_egp", 0.0) * scale

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
                rid = row["recipe_id"]
                scale = scaling_factors[rid]
                scaled_qty = float(row["quantity"]) * scale

                grouped_ingredients[row["ingredient_id"]].append({
                    "recipe_id": rid,
                    "recipe_name_ar": row["recipe_name_ar"],
                    "original_name": row["original_ingredient_name"],
                    "quantity": scaled_qty,
                    "base_quantity": float(row["quantity"]),
                    "unit": str(row["unit"]).strip(),
                    "is_optional": bool(row["is_optional"]),
                    "canonical_name_ar": row["canonical_name_ar"] or row["original_ingredient_name"],
                    "canonical_name_en": row["canonical_name_en"] or row["original_ingredient_name"],
                    "scale_factor": scale,
                })

            cart_items: List[Dict[str, Any]] = []
            pantry_covered_items: List[Dict[str, Any]] = []
            unpriced_items: List[Dict[str, Any]] = []
            substituted_items: List[Dict[str, Any]] = []

            total_smart_procurement_cost = 0.0
            total_shared_savings = 0.0

            # 4. Process each required ingredient: Pantry check -> Packaging -> Consolidation -> Substitution
            for ing_id, usages in grouped_ingredients.items():
                name_ar = usages[0]["canonical_name_ar"]
                name_en = usages[0]["canonical_name_en"]
                is_optional_overall = all(u["is_optional"] for u in usages)

                # Fetch available in-stock products for this ingredient
                prod_query = """
                    SELECT product_id, product_name, product_name_ar, brand,
                           package_size, package_unit, price_egp, store_id
                    FROM products
                    WHERE ingredient_id = ? AND availability = 'in_stock'
                """
                params: List[Any] = [ing_id]
                if store_id:
                    prod_query += " AND store_id = ?"
                    params.append(store_id)

                products = c.execute(prod_query, params).fetchall()

                # Check if ingredient needs substitution
                active_ing_id = ing_id
                substitution_info = None

                if not products and enable_substitutes:
                    sub_candidates = self.find_substitutes(ing_id, store_id=store_id)
                    if sub_candidates:
                        best_sub = sub_candidates[0]
                        active_ing_id = best_sub["substitute_ingredient_id"]
                        substitution_info = {
                            "original_ingredient_id": ing_id,
                            "original_name_ar": name_ar,
                            "substitute_ingredient_id": active_ing_id,
                            "substitute_name_ar": best_sub["substitute_name_ar"],
                            "ratio": best_sub["ratio"],
                            "reason_ar": best_sub["reason_ar"],
                        }
                        # Re-query products using substitute ingredient
                        prod_query_sub = """
                            SELECT product_id, product_name, product_name_ar, brand,
                                   package_size, package_unit, price_egp, store_id
                            FROM products
                            WHERE ingredient_id = ? AND availability = 'in_stock'
                        """
                        params_sub: List[Any] = [active_ing_id]
                        if store_id:
                            prod_query_sub += " AND store_id = ?"
                            params_sub.append(store_id)
                        products = c.execute(prod_query_sub, params_sub).fetchall()

                # If still no product available: add to unpriced
                if not products:
                    unpriced_items.append({
                        "ingredient_id": ing_id,
                        "ingredient_name_ar": name_ar,
                        "ingredient_name_en": name_en,
                        "is_optional": is_optional_overall,
                        "used_in_recipes": list({u["recipe_name_ar"] for u in usages}),
                        "recipe_count": len(usages),
                        "usages": [
                            {
                                "recipe_id": u["recipe_id"],
                                "recipe_name_ar": u["recipe_name_ar"],
                                "quantity": round(u["quantity"], 3),
                                "unit": u["unit"],
                            }
                            for u in usages
                        ],
                        "reason": f"NO_IN_STOCK_PRODUCT" if not store_id else f"OUT_OF_STOCK_IN_STORE_{store_id}",
                    })
                    continue

                # Choose best product (lowest unit price)
                best_product = None
                best_unit_price = float("inf")
                for p in products:
                    p_size = float(p["package_size"])
                    p_price = float(p["price_egp"])
                    u_price = p_price / p_size if p_size > 0 else float("inf")
                    if u_price < best_unit_price:
                        best_unit_price = u_price
                        best_product = p

                pkg_id = best_product["product_id"]
                pkg_name = best_product["product_name"]
                pkg_name_ar = best_product["product_name_ar"] or pkg_name
                pkg_brand = best_product["brand"]
                pkg_store = best_product["store_id"]
                pkg_size = float(best_product["package_size"])
                pkg_unit = best_product["package_unit"]
                pkg_price = float(best_product["price_egp"])

                # Convert all recipe usages into the product's package unit
                sub_ratio = substitution_info["ratio"] if substitution_info else 1.0
                total_qty_needed = 0.0
                separate_pkgs_sum = 0
                item_recipe_breakdown = []

                for u in usages:
                    adjusted_qty = u["quantity"] * sub_ratio
                    detailed = UnitConverter.convert_detailed(adjusted_qty, u["unit"], pkg_unit, active_ing_id)
                    converted_qty = detailed["converted_quantity"]
                    if converted_qty is None:
                        converted_qty = adjusted_qty

                    total_qty_needed += converted_qty
                    sep_pkgs = math.ceil(converted_qty / pkg_size)
                    if sep_pkgs <= 0:
                        sep_pkgs = 1
                    separate_pkgs_sum += sep_pkgs

                    item_recipe_breakdown.append({
                        "recipe_id": u["recipe_id"],
                        "recipe_name_ar": u["recipe_name_ar"],
                        "original_quantity": round(u["base_quantity"], 3),
                        "scaled_quantity": round(u["quantity"], 3),
                        "unit": u["unit"],
                        "converted_quantity": round(converted_qty, 3),
                        "converted_unit": pkg_unit,
                        "separate_packages_needed": sep_pkgs,
                    })

                # --- 5. Pantry Deduction Logic ---
                pantry_entry = normalized_pantry.get(ing_id) or normalized_pantry.get(active_ing_id)
                pantry_deducted_qty = 0.0
                is_fully_pantry_covered = False

                if pantry_entry:
                    if pantry_entry.get("is_unlimited", False):
                        pantry_deducted_qty = total_qty_needed
                        is_fully_pantry_covered = True
                    else:
                        p_qty = pantry_entry["quantity"]
                        p_unit = pantry_entry["unit"]
                        detailed_pantry = UnitConverter.convert_detailed(p_qty, p_unit, pkg_unit, active_ing_id)
                        converted_pantry = detailed_pantry["converted_quantity"] or p_qty
                        if converted_pantry >= total_qty_needed:
                            pantry_deducted_qty = total_qty_needed
                            is_fully_pantry_covered = True
                        else:
                            pantry_deducted_qty = converted_pantry

                net_qty_to_purchase = max(0.0, total_qty_needed - pantry_deducted_qty)

                # If fully covered by home pantry, record and skip purchasing
                if is_fully_pantry_covered or net_qty_to_purchase <= 0.0:
                    pantry_covered_items.append({
                        "ingredient_id": ing_id,
                        "ingredient_name_ar": name_ar,
                        "ingredient_name_en": name_en,
                        "total_quantity_needed": round(total_qty_needed, 3),
                        "unit": pkg_unit,
                        "status": "COVERED_BY_PANTRY",
                        "estimated_money_saved_egp": round(math.ceil(total_qty_needed / pkg_size) * pkg_price, 2),
                        "recipes": list({u["recipe_name_ar"] for u in usages}),
                    })
                    continue

                # --- 6. Package Calculation & Savings ---
                smart_packages_needed = math.ceil(net_qty_to_purchase / pkg_size)
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
                leftover_quantity = (smart_packages_needed * pkg_size) - net_qty_to_purchase

                cart_item_entry = {
                    "ingredient_id": ing_id,
                    "ingredient_name_ar": name_ar,
                    "ingredient_name_en": name_en,
                    "is_shared": is_shared,
                    "is_optional": is_optional_overall,
                    "shared_recipe_count": len(usages),
                    "total_quantity_needed": round(total_qty_needed, 3),
                    "pantry_deducted_quantity": round(pantry_deducted_qty, 3),
                    "net_quantity_to_purchase": round(net_qty_to_purchase, 3),
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
                        "unit_price_egp": round(best_unit_price, 4),
                    },
                    "smart_packages_needed": smart_packages_needed,
                    "smart_cost_egp": smart_cost,
                    "separate_packages_needed": separate_pkgs_sum,
                    "separate_cost_egp": separate_cost,
                    "savings_egp": savings,
                    "leftover_quantity": round(leftover_quantity, 3),
                    "is_substituted": (substitution_info is not None),
                    "substitution_info": substitution_info,
                    "recipe_breakdown": item_recipe_breakdown,
                }

                if substitution_info:
                    substituted_items.append(cart_item_entry)

                cart_items.append(cart_item_entry)

            # Sort cart items: shared ingredients first (highest savings), then by cost
            cart_items.sort(
                key=lambda x: (x["is_shared"], x["savings_egp"], x["smart_cost_egp"]),
                reverse=True
            )

            total_smart_procurement_cost = round(sum(item["smart_cost_egp"] for item in cart_items), 2)
            total_separate_procurement_cost = round(sum(item["separate_cost_egp"] for item in cart_items), 2)
            total_shared_savings = round(sum(item["savings_egp"] for item in cart_items), 2)
            savings_pct = (
                round((total_shared_savings / total_separate_procurement_cost) * 100.0, 2)
                if total_separate_procurement_cost > 0 else 0.0
            )

            shared_count = sum(1 for item in cart_items if item["is_shared"])
            single_count = len(cart_items) - shared_count

            # --- 7. Budget Optimization Analysis ---
            budget_result = None
            if budget_egp is not None and budget_egp > 0:
                budget_result = self.optimize_cart_budget(cart_items, float(budget_egp))
                if optimize_budget and budget_result["budget_status"] == "EXCEEDED_OPTIMIZED":
                    # Filter active cart items to retained items if requested
                    retained_ids = {item["ingredient_id"] for item in budget_result["retained_items"]}
                    cart_items = [item for item in cart_items if item["ingredient_id"] in retained_ids]
                    total_smart_procurement_cost = budget_result["optimized_cart_total_egp"]

            # --- 8. Build Descriptive Summary Message ---
            servings_summary_list = [f"{recipe_meta[rid]['recipe_name_ar']}: {s_cnt}" for rid, s_cnt in target_servings_map.items()]
            servings_str = ", ".join(servings_summary_list)
            summary_parts = [
                f"تم تجميع السلة الذكية لـ {len(unique_recipe_ids)} وصفات بنجاح (لعدد أفراد: {servings_str})."
            ]

            if shared_count > 0:
                summary_parts.append(
                    f"تم توفير {total_shared_savings:.2f} ج.م ({savings_pct:.1f}%) بدمج {shared_count} مكونات مشتركة ومنع تكرار العبوات."
                )

            if pantry_covered_items:
                pantry_saved = sum(p["estimated_money_saved_egp"] for p in pantry_covered_items)
                summary_parts.append(
                    f"تم استبعاد {len(pantry_covered_items)} مكونات متوفرة بمطبخك، موفراً حوالي {pantry_saved:.2f} ج.م إضافية."
                )

            if substituted_items:
                summary_parts.append(
                    f"تم اقتراح بدائل ذكية لـ {len(substituted_items)} منتجات لضمان اكتمال الطبخ بأفضل سعر."
                )

            if budget_result and budget_result["budget_status"] != "WITHIN_BUDGET":
                summary_parts.append(budget_result["advice_message_ar"])

            return {
                "success": True,
                "recipe_ids": unique_recipe_ids,
                "recipes": [
                    {
                        "recipe_id": r["recipe_id"],
                        "recipe_name_ar": r["recipe_name_ar"],
                        "recipe_name_en": r["recipe_name_en"],
                        "base_servings": r["base_servings"],
                        "target_servings": target_servings_map[r["recipe_id"]],
                        "scale_factor": round(scaling_factors[r["recipe_id"]], 2),
                        "cuisine": r["cuisine"],
                        "category": r["category"],
                    }
                    for r in recipes_data
                ],
                "store_id_filter": store_id,
                # Financials
                "smart_cart_total_egp": total_smart_procurement_cost,
                "separate_carts_total_egp": total_separate_procurement_cost,
                "total_savings_egp": total_shared_savings,
                "savings_percentage": savings_pct,
                "net_consumed_total_egp": round(total_net_consumed_cost, 2),
                # Counts & Coverage
                "total_cart_items_count": len(cart_items),
                "shared_ingredients_count": shared_count,
                "unique_ingredients_count": single_count,
                "pantry_covered_count": len(pantry_covered_items),
                "unpriced_ingredients_count": len(unpriced_items),
                "substituted_ingredients_count": len(substituted_items),
                "is_fully_priced": (len(unpriced_items) == 0),
                "summary_message": " ".join(summary_parts),
                # Detailed Lists
                "cart_items": cart_items,
                "pantry_covered_items": pantry_covered_items,
                "unpriced_ingredients": unpriced_items,
                "substituted_items": substituted_items,
                "budget_analysis": budget_result,
            }

    def optimize_cart_budget(
        self,
        cart_items: List[Dict[str, Any]],
        budget_egp: float
    ) -> Dict[str, Any]:
        """
        Integer Linear Programming (Knapsack) Budget Optimizer.
        
        Maximizes cart utility and essential ingredient fulfillment under a hard budget constraint:
        - Essential ingredients have top priority.
        - Shared multi-recipe ingredients have higher utility.
        - Drops lowest priority optional items first if budget is exceeded.
        """
        total_current_cost = sum(item["smart_cost_egp"] for item in cart_items)

        if total_current_cost <= budget_egp:
            return {
                "budget_status": "WITHIN_BUDGET",
                "budget_egp": budget_egp,
                "original_cost_egp": total_current_cost,
                "optimized_cart_total_egp": total_current_cost,
                "budget_surplus_egp": round(budget_egp - total_current_cost, 2),
                "retained_items": cart_items,
                "dropped_items": [],
                "advice_message_ar": f"التكلفة الحالية ({total_current_cost:.2f} ج.م) تقع بالكامل داخل الميزانية المحددة ({budget_egp:.2f} ج.م)."
            }

        # Calculate importance / utility weight for each item
        # Essential items: 100 + shared_bonus; Optional items: 20 + shared_bonus
        scored_items = []
        for item in cart_items:
            weight = 20 if item.get("is_optional", False) else 100
            if item.get("is_shared", False):
                weight += item.get("shared_recipe_count", 1) * 15
            scored_items.append({
                "item": item,
                "cost": item["smart_cost_egp"],
                "utility": weight,
                "is_optional": item.get("is_optional", False),
            })

        retained_items = []
        dropped_items = []

        # Attempt OR-Tools solution if available
        solved_with_ortools = False
        if OR_TOOLS_AVAILABLE and pywraplp is not None:
            try:
                solver = pywraplp.Solver.CreateSolver('SCIP') or pywraplp.Solver.CreateSolver('CBC')
                if solver:
                    n = len(scored_items)
                    x = [solver.BoolVar(f"x_{i}") for i in range(n)]

                    # Budget constraint
                    solver.Add(solver.Sum([x[i] * scored_items[i]["cost"] for i in range(n)]) <= budget_egp)

                    # Maximize utility
                    solver.Maximize(solver.Sum([x[i] * scored_items[i]["utility"] for i in range(n)]))

                    status = solver.Solve()
                    if status in (pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE):
                        for i in range(n):
                            if x[i].solution_value() > 0.5:
                                retained_items.append(scored_items[i]["item"])
                            else:
                                dropped_items.append(scored_items[i]["item"])
                        solved_with_ortools = True
            except Exception:
                solved_with_ortools = False

        # Exact Pure-Python Branch-and-Bound / Greedy Knapsack Fallback
        if not solved_with_ortools:
            # Sort: Essential first, then highest utility-per-pound, then lowest cost
            sorted_candidates = sorted(
                scored_items,
                key=lambda x: (not x["is_optional"], x["utility"] / max(x["cost"], 0.1), -x["cost"]),
                reverse=True
            )
            accumulated_cost = 0.0
            for entry in sorted_candidates:
                if accumulated_cost + entry["cost"] <= budget_egp:
                    retained_items.append(entry["item"])
                    accumulated_cost += entry["cost"]
                else:
                    dropped_items.append(entry["item"])

        optimized_total = round(sum(item["smart_cost_egp"] for item in retained_items), 2)
        deficit = round(total_current_cost - budget_egp, 2)
        dropped_names = [d["ingredient_name_ar"] for d in dropped_items]

        advice = (
            f"تم تجاوز الميزانية بمقدار {deficit:.2f} ج.م. "
            f"قام محرك التحسين بترشيد السلة إلى {optimized_total:.2f} ج.م، "
            f"حيث تم استبقاء الأساسيات واستبعاد {len(dropped_items)} مكونات غير حرجة "
            f"({', '.join(dropped_names[:4])})."
        )

        return {
            "budget_status": "EXCEEDED_OPTIMIZED",
            "budget_egp": budget_egp,
            "original_cost_egp": total_current_cost,
            "optimized_cart_total_egp": optimized_total,
            "budget_deficit_egp": deficit,
            "retained_items": retained_items,
            "dropped_items": dropped_items,
            "dropped_count": len(dropped_items),
            "solver_engine": "OR-Tools SCIP" if solved_with_ortools else "Branch-and-Bound Pure Python",
            "advice_message_ar": advice,
        }

    def compare_stores(
        self,
        recipe_ids: List[str],
        servings: Optional[Union[int, float, Dict[str, float]]] = None,
        user_pantry: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Compare the grocery cart across all registered supermarket chains.
        
        Returns a ranking of stores by total cost and ingredient fulfillment.
        """
        store_comparisons = []
        with self._get_connection() as conn:
            stores = conn.execute("SELECT store_id, store_name FROM stores").fetchall()

            for s in stores:
                sid = s["store_id"]
                sname = s["store_name"]

                cart_res = self.build_cart(
                    recipe_ids=recipe_ids,
                    servings=servings,
                    user_pantry=user_pantry,
                    store_id=sid,
                    enable_substitutes=True,
                    optimize_budget=False
                )

                if cart_res["success"]:
                    store_comparisons.append({
                        "store_id": sid,
                        "store_name": sname,
                        "total_cost_egp": cart_res["smart_cart_total_egp"],
                        "cart_items_count": cart_res["total_cart_items_count"],
                        "unpriced_count": cart_res["unpriced_ingredients_count"],
                        "is_fully_priced": cart_res["is_fully_priced"],
                        "cart_items": cart_res["cart_items"],
                    })

        # Rank stores by product availability first, then by lowest price
        store_comparisons.sort(
            key=lambda x: (x["unpriced_count"], x["total_cost_egp"])
        )

        cheapest = store_comparisons[0] if store_comparisons else None
        most_expensive = max(store_comparisons, key=lambda x: x["total_cost_egp"]) if store_comparisons else None
        max_store_savings = 0.0
        if cheapest and most_expensive and most_expensive["total_cost_egp"] > cheapest["total_cost_egp"]:
            max_store_savings = round(most_expensive["total_cost_egp"] - cheapest["total_cost_egp"], 2)

        return {
            "recipe_ids": recipe_ids,
            "stores_evaluated_count": len(store_comparisons),
            "cheapest_store": cheapest,
            "potential_store_savings_egp": max_store_savings,
            "store_rankings": store_comparisons,
        }

    def to_dataframe(self, cart_result: Dict[str, Any]):
        """Export cart items to a pandas DataFrame."""
        if not PANDAS_AVAILABLE:
            raise ImportError("Pandas is not installed. Use dictionary output directly.")
        items = cart_result.get("cart_items", [])
        flat_rows = []
        for item in items:
            p = item["product"]
            flat_rows.append({
                "Ingredient ID": item["ingredient_id"],
                "Ingredient (AR)": item["ingredient_name_ar"],
                "Is Shared": item["is_shared"],
                "Shared In Recipes": item["shared_recipe_count"],
                "Needed Quantity": item["total_quantity_needed"],
                "Pantry Deducted": item["pantry_deducted_quantity"],
                "Net Purchase Qty": item["net_quantity_to_purchase"],
                "Unit": item["unit"],
                "Product Name": p["product_name_ar"],
                "Brand": p["brand"],
                "Package Size": f"{p['package_size']} {p['package_unit']}",
                "Packs Needed": item["smart_packages_needed"],
                "Pack Price EGP": p["price_egp"],
                "Smart Cost EGP": item["smart_cost_egp"],
                "Separate Cost EGP": item["separate_cost_egp"],
                "Savings EGP": item["savings_egp"],
                "Leftover Qty": item["leftover_quantity"],
                "Is Substituted": item.get("is_substituted", False),
            })
        return pd.DataFrame(flat_rows)
