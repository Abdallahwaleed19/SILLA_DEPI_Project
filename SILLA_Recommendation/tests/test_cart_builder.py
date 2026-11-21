"""
SILLA_Recommendation/tests/test_cart_builder.py
===============================================
Comprehensive Unit Test Suite for SILLA CartBuilder (Jana Shalaby's Module):
- Servings scaling (عدد الأفراد)
- Pantry deduction & exclusion (استبعاد المكونات بالمنزل)
- Multi-recipe ingredient consolidation & savings (دمج المكونات المشتركة)
- Product packaging & leftover calculation (مطابقة المنتجات والعبوات)
- Budget optimization via OR-Tools / Knapsack (مراعاة الميزانية)
- Out-of-stock & culinary substitutions (التعامل مع غير المتاح والبدائل)
- Multi-store supermarket comparison (مقارنة المتاجر)
"""

import unittest
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from SILLA_Recommendation.config import STAGING_DB_PATH
from SILLA_Recommendation.cart_builder import CartBuilder


class TestCartBuilder(unittest.TestCase):
    """Test suite for CartBuilder business logic and optimization."""

    @classmethod
    def setUpClass(cls):
        cls.builder = CartBuilder(db_path=STAGING_DB_PATH)

    def test_single_recipe_default_servings(self):
        """Verify baseline cart generation for a single recipe."""
        res = self.builder.build_cart(["R0001"])
        self.assertTrue(res["success"])
        self.assertEqual(len(res["recipes"]), 1)
        self.assertGreater(res["smart_cart_total_egp"], 0.0)
        self.assertEqual(res["shared_ingredients_count"], 0)
        self.assertEqual(res["total_savings_egp"], 0.0)

    def test_servings_scaling_up(self):
        """Verify scaling quantities up by servings factor."""
        # Base servings of R0001 is 6
        res_base = self.builder.build_cart(["R0001"])
        res_scaled = self.builder.build_cart(["R0001"], servings=12)

        self.assertTrue(res_scaled["success"])
        self.assertEqual(res_scaled["recipes"][0]["target_servings"], 12)
        self.assertEqual(res_scaled["recipes"][0]["scale_factor"], 2.0)

        # Total cost for 12 servings should be greater than or equal to base cost
        self.assertGreaterEqual(res_scaled["smart_cart_total_egp"], res_base["smart_cart_total_egp"])

        # Check item quantities doubled
        base_item = next(i for i in res_base["cart_items"] if i["ingredient_id"] == "ING0089")
        scaled_item = next(i for i in res_scaled["cart_items"] if i["ingredient_id"] == "ING0089")
        self.assertAlmostEqual(scaled_item["total_quantity_needed"], base_item["total_quantity_needed"] * 2.0, places=2)

    def test_servings_scaling_per_recipe_dict(self):
        """Verify individual per-recipe servings dictionary."""
        res = self.builder.build_cart(
            ["R0001", "R0007"],
            servings={"R0001": 3, "R0007": 8}
        )
        self.assertTrue(res["success"])
        r1 = next(r for r in res["recipes"] if r["recipe_id"] == "R0001")
        r7 = next(r for r in res["recipes"] if r["recipe_id"] == "R0007")
        self.assertEqual(r1["target_servings"], 3)
        self.assertEqual(r7["target_servings"], 8)

    def test_pantry_exclusion_by_arabic_name(self):
        """Verify pantry items passed as Arabic names are excluded from purchase."""
        res_no_pantry = self.builder.build_cart(["R0001"])
        res_with_pantry = self.builder.build_cart(
            ["R0001"],
            user_pantry=["بصل أصفر", "فلفل أسود"]
        )

        self.assertTrue(res_with_pantry["success"])
        self.assertGreater(res_with_pantry["pantry_covered_count"], 0)

        # Pantry covered items should not be in the purchase cart
        cart_ing_ids = [i["ingredient_id"] for i in res_with_pantry["cart_items"]]
        self.assertNotIn("ING0139", cart_ing_ids)  # Onion should be covered
        self.assertNotIn("ING0012", cart_ing_ids)  # Black pepper should be covered

        # Cost with pantry must be strictly less than without pantry
        self.assertLess(res_with_pantry["smart_cart_total_egp"], res_no_pantry["smart_cart_total_egp"])

    def test_pantry_partial_quantity_deduction(self):
        """Verify pantry with partial quantity reduces net purchase requirement."""
        # Onion required in R0001 is 2 pieces = 250g
        res = self.builder.build_cart(
            ["R0001"],
            user_pantry={"ING0139": {"quantity": 125.0, "unit": "g"}}
        )
        self.assertTrue(res["success"])
        onion_item = next(i for i in res["cart_items"] if i["ingredient_id"] == "ING0139")
        self.assertAlmostEqual(onion_item["pantry_deducted_quantity"], 125.0, places=1)
        self.assertAlmostEqual(onion_item["net_quantity_to_purchase"], 125.0, places=1)

    def test_multi_recipe_consolidation_and_savings(self):
        """Verify multi-recipe ingredient aggregation and positive savings."""
        res = self.builder.build_cart(["R0001", "R0007"])
        self.assertTrue(res["success"])
        self.assertEqual(len(res["recipes"]), 2)

        # Consistency check: separate - smart == savings
        self.assertAlmostEqual(
            res["separate_carts_total_egp"] - res["smart_cart_total_egp"],
            res["total_savings_egp"],
            places=2
        )
        self.assertGreater(res["total_savings_egp"], 50.0)
        self.assertGreater(res["shared_ingredients_count"], 0)

    def test_budget_optimization_within_budget(self):
        """Verify cart behavior when budget is generous."""
        res = self.builder.build_cart(["R0001"], budget_egp=5000.0)
        b = res["budget_analysis"]
        self.assertIsNotNone(b)
        self.assertEqual(b["budget_status"], "WITHIN_BUDGET")
        self.assertEqual(len(b["dropped_items"]), 0)
        self.assertGreater(b["budget_surplus_egp"], 0.0)

    def test_budget_optimization_exceeded_drops_optional(self):
        """Verify knapsack optimizer enforces budget limit and drops optional items first."""
        # Unconstrained cost is ~386 EGP, set budget to 75 EGP
        res = self.builder.build_cart(["R0001"], budget_egp=75.0, optimize_budget=True)
        b = res["budget_analysis"]
        self.assertIsNotNone(b)
        self.assertEqual(b["budget_status"], "EXCEEDED_OPTIMIZED")
        self.assertLessEqual(res["smart_cart_total_egp"], 75.0)
        self.assertGreater(len(b["dropped_items"]), 0)
        self.assertIn("EXCEEDED_OPTIMIZED", b["budget_status"])

    def test_culinary_substitutions_engine(self):
        """Verify out-of-stock substitute finder suggests realistic culinary alternatives."""
        # Test finding substitute for butter (ING0017)
        subs = self.builder.find_substitutes("ING0017")
        self.assertGreater(len(subs), 0)
        sub_ids = [s["substitute_ingredient_id"] for s in subs]
        self.assertIn("ING0126", sub_ids)  # Vegetable oil is a culinary substitute for butter

    def test_multi_store_comparison(self):
        """Verify store ranking and identification of most economical store."""
        res = self.builder.compare_stores(["R0001"])
        self.assertGreaterEqual(res["stores_evaluated_count"], 4)
        self.assertIsNotNone(res["cheapest_store"])
        self.assertIn("store_name", res["cheapest_store"])
        self.assertGreater(res["cheapest_store"]["total_cost_egp"], 0.0)

    def test_empty_recipe_ids_error(self):
        """Verify clean error response on empty input."""
        res = self.builder.build_cart([])
        self.assertFalse(res["success"])
        self.assertEqual(res["smart_cart_total_egp"], 0.0)

    def test_invalid_recipe_id_error(self):
        """Verify clean error response on invalid recipe ID."""
        res = self.builder.build_cart(["R9999"])
        self.assertFalse(res["success"])
        self.assertIn("missing_recipe_ids", res)


if __name__ == "__main__":
    unittest.main()
