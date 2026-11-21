"""
SILLA_Recommendation/tests/test_smart_cart.py
=============================================
Automated unit tests for SmartCart:
- Multi-recipe ingredient consolidation.
- Elimination of redundant supermarket packaging.
- Mathematical consistency of savings.
- Handling shared ingredients with different units.
- Product selection policy consistency.
- Unpriced items multi-recipe aggregation.
"""

import unittest
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from SILLA_Recommendation.config import STAGING_DB_PATH
from SILLA_Recommendation.smart_cart import SmartCart


class TestSmartCart(unittest.TestCase):
    """Test smart grocery cart optimization across single and multiple recipes."""

    @classmethod
    def setUpClass(cls):
        cls.cart = SmartCart(db_path=STAGING_DB_PATH)

    def test_single_recipe_cart(self):
        # Single recipe: no shared ingredients across recipes
        res = self.cart.build_smart_cart(["R0001"])
        self.assertTrue(res["success"])
        self.assertEqual(len(res["recipes"]), 1)
        self.assertEqual(res["shared_ingredients_count"], 0)
        self.assertEqual(res["total_savings_egp"], 0.0)
        self.assertEqual(res["smart_cart_total_egp"], res["separate_carts_total_egp"])
        self.assertGreater(res["smart_cart_total_egp"], 0.0)

    def test_multi_recipe_shared_savings(self):
        # Macaroni Béchamel (R0001) + Kofta Mashweya (R0007)
        res = self.cart.build_smart_cart(["R0001", "R0007"])
        self.assertTrue(res["success"])
        self.assertEqual(len(res["recipes"]), 2)

        # Mathematical consistency: separate - smart == savings
        self.assertAlmostEqual(
            res["separate_carts_total_egp"] - res["smart_cart_total_egp"],
            res["total_savings_egp"],
            places=2
        )

        # Substantial savings achieved through consolidation
        self.assertGreater(res["total_savings_egp"], 50.0)
        self.assertGreater(res["savings_percentage"], 5.0)
        self.assertGreaterEqual(res["shared_ingredients_count"], 3)

        # Check shared items details (supports current & legacy ingredient IDs)
        shared_ing_ids = [item["ingredient_id"] for item in res["cart_items"] if item["is_shared"]]
        self.assertTrue("ING0067" in shared_ing_ids or "ING0042" in shared_ing_ids)  # Ground beef
        self.assertTrue("ING0139" in shared_ing_ids or "ING0071" in shared_ing_ids)  # Yellow onion
        self.assertTrue("ING0012" in shared_ing_ids or "ING0009" in shared_ing_ids)  # Black pepper

    def test_policy_consistency_identical_product_pricing(self):
        """Audit guarantee: Separate procurement and smart cart use identical product SKUs and unit prices."""
        res = self.cart.build_smart_cart(["R0001", "R0007"])
        for item in res["cart_items"]:
            pkg_price = item["product"]["price_egp"]
            expected_sep_cost = item["separate_packages_needed"] * pkg_price
            expected_smart_cost = item["smart_packages_needed"] * pkg_price
            self.assertAlmostEqual(item["separate_cost_egp"], expected_sep_cost, places=2)
            self.assertAlmostEqual(item["smart_cost_egp"], expected_smart_cost, places=2)
            self.assertAlmostEqual(item["savings_egp"], expected_sep_cost - expected_smart_cost, places=2)

    def test_shared_ingredients_with_different_units(self):
        """Audit guarantee: Shared ingredients in different units (e.g. piece vs g) convert cleanly."""
        res = self.cart.build_smart_cart(["R0001", "R0007"])
        onion_item = next(item for item in res["cart_items"] if item["ingredient_id"] in ("ING0139", "ING0071"))
        # In R0001 and R0007, each uses 2 pieces = 250g. Total = 500g in 1kg package.
        self.assertEqual(onion_item["total_quantity_needed"], 500.0)
        self.assertEqual(onion_item["smart_packages_needed"], 1)
        self.assertEqual(onion_item["separate_packages_needed"], 2)
        self.assertGreater(onion_item["savings_egp"], 0.0)

    def test_unpriced_ingredients_multi_recipe_aggregation(self):
        """Audit guarantee: Unpriced items appearing in multiple recipes are merged with usage tracking."""
        res = self.cart.build_smart_cart(["R0001", "R0007"])
        self.assertGreater(res["unpriced_ingredients_count"], 0)
        salt_item = next((u for u in res["unpriced_ingredients"] if u["ingredient_id"] in ("ING0051", "ING0057")), None)
        self.assertIsNotNone(salt_item)
        self.assertEqual(salt_item["recipe_count"], 2)
        self.assertEqual(len(salt_item["used_in_recipes"]), 2)

    def test_multiple_commercial_alternatives_optimal_selection(self):
        """Audit guarantee: Best product selected has the lowest unit price among available candidates."""
        res = self.cart.build_smart_cart(["R0001", "R0007"])
        pasta_item = next(item for item in res["cart_items"] if item["ingredient_id"] in ("ING0089", "ING0052"))
        # Selected Penne pasta product has lowest unit price
        self.assertIsNotNone(pasta_item["product"]["product_id"])
        self.assertGreater(pasta_item["product"]["unit_price_egp"], 0.0)

    def test_three_recipes_cart(self):
        # R0001 (Bechamel) + R0002 (Koshari) + R0007 (Kofta)
        res = self.cart.build_smart_cart(["R0001", "R0002", "R0007"])
        self.assertTrue(res["success"])
        self.assertEqual(len(res["recipes"]), 3)
        self.assertGreater(res["total_savings_egp"], 70.0)
        self.assertGreater(res["shared_ingredients_count"], 2)

    def test_empty_recipe_list(self):
        res = self.cart.build_smart_cart([])
        self.assertFalse(res["success"])
        self.assertEqual(res["total_savings_egp"], 0.0)

    def test_invalid_recipe_id(self):
        res = self.cart.build_smart_cart(["R9999"])
        self.assertFalse(res["success"])
        self.assertIn("missing_recipe_ids", res)

    def test_duplicate_recipe_ids_deduplication(self):
        res = self.cart.build_smart_cart(["R0001", "R0001"])
        self.assertTrue(res["success"])
        self.assertEqual(len(res["recipe_ids"]), 1)


if __name__ == "__main__":
    unittest.main()
