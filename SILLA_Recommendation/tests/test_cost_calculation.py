"""
SILLA_Recommendation/tests/test_cost_calculation.py
===================================================
Automated unit tests for UnitConverter and CostCalculator:
- Exact vs Approximate vs Unsupported classification.
- Documented variance tracking.
- Empirical recipe costs on silla_staging.db.
- Coverage dependency on required ingredients (not product counts).
- Procurement coverage guarantee (packages * size >= required).
"""

import unittest
import math
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from SILLA_Recommendation.config import STAGING_DB_PATH
from SILLA_Recommendation.cost_calculator import UnitConverter, CostCalculator


class TestUnitConverter(unittest.TestCase):
    """Test unit conversions across mass, volume, piece weights, and culinary units."""

    def test_exact_unit_match(self):
        det = UnitConverter.convert_detailed(100.0, "g", "g")
        self.assertEqual(det["converted_quantity"], 100.0)
        self.assertEqual(det["classification"], "EXACT")
        self.assertEqual(det["estimated_variance_pct"], 0.0)
        self.assertTrue(det["is_supported"])

        det_ml = UnitConverter.convert_detailed(250.0, "ml", "ml")
        self.assertEqual(det_ml["converted_quantity"], 250.0)
        self.assertEqual(det_ml["classification"], "EXACT")
        self.assertEqual(det_ml["estimated_variance_pct"], 0.0)

    def test_standard_volume_conversions_exact(self):
        # 1 tsp = 5 ml (definition)
        det = UnitConverter.convert_detailed(2.0, "tsp", "ml")
        self.assertAlmostEqual(det["converted_quantity"], 10.0, places=2)
        self.assertEqual(det["classification"], "EXACT")
        self.assertEqual(det["estimated_variance_pct"], 0.0)

        # 1 tbsp = 15 ml (definition)
        det = UnitConverter.convert_detailed(3.0, "tbsp", "ml")
        self.assertAlmostEqual(det["converted_quantity"], 45.0, places=2)
        self.assertEqual(det["classification"], "EXACT")

        # 1 cup = 240 ml (standard legal/metric cup)
        det = UnitConverter.convert_detailed(1.5, "cup", "ml")
        self.assertAlmostEqual(det["converted_quantity"], 360.0, places=2)
        self.assertEqual(det["classification"], "EXACT")

        # 1 L = 1000 ml (SI)
        det = UnitConverter.convert_detailed(0.5, "l", "ml")
        self.assertAlmostEqual(det["converted_quantity"], 500.0, places=2)
        self.assertEqual(det["classification"], "EXACT")

    def test_standard_mass_conversions_exact(self):
        # 1 kg = 1000 g (SI)
        det = UnitConverter.convert_detailed(1.25, "kg", "g")
        self.assertAlmostEqual(det["converted_quantity"], 1250.0, places=2)
        self.assertEqual(det["classification"], "EXACT")
        self.assertEqual(det["estimated_variance_pct"], 0.0)

        # 500 g = 0.5 kg (SI)
        det = UnitConverter.convert_detailed(500.0, "g", "kg")
        self.assertAlmostEqual(det["converted_quantity"], 0.5, places=3)
        self.assertEqual(det["classification"], "EXACT")

    def test_culinary_volume_to_mass_approximate(self):
        # 1 tsp spice ~ 5g (approximate bulk density)
        det = UnitConverter.convert_detailed(2.0, "tsp", "g")
        self.assertAlmostEqual(det["converted_quantity"], 10.0, places=2)
        self.assertEqual(det["classification"], "APPROXIMATE")
        self.assertGreater(det["estimated_variance_pct"], 0.0)
        self.assertIn("Bulk Density", det["source_standard"])

        # 1 tbsp paste/butter ~ 15g
        det = UnitConverter.convert_detailed(2.0, "tbsp", "g")
        self.assertAlmostEqual(det["converted_quantity"], 30.0, places=2)
        self.assertEqual(det["classification"], "APPROXIMATE")

    def test_clove_and_bunch_approximate(self):
        # 1 clove garlic ~ 4g
        det = UnitConverter.convert_detailed(3.0, "clove", "g")
        self.assertAlmostEqual(det["converted_quantity"], 12.0, places=2)
        self.assertEqual(det["classification"], "APPROXIMATE")
        self.assertEqual(det["estimated_variance_pct"], 25.0)

        # 1 bunch herbs ~ 50g
        det = UnitConverter.convert_detailed(2.0, "bunch", "g")
        self.assertAlmostEqual(det["converted_quantity"], 100.0, places=2)
        self.assertEqual(det["classification"], "APPROXIMATE")
        self.assertEqual(det["estimated_variance_pct"], 30.0)

    def test_produce_piece_to_gram_approximate(self):
        # Yellow Onion ING0071 ~ 125g
        det = UnitConverter.convert_detailed(2.0, "piece", "g", ingredient_id="ING0071")
        self.assertAlmostEqual(det["converted_quantity"], 250.0, places=2)
        self.assertEqual(det["classification"], "APPROXIMATE")
        self.assertEqual(det["estimated_variance_pct"], 25.0)
        self.assertIn("125.0g", det["source_standard"])

        # Potato ING0053 ~ 150g
        det = UnitConverter.convert_detailed(3.0, "piece", "g", ingredient_id="ING0053")
        self.assertAlmostEqual(det["converted_quantity"], 450.0, places=2)
        self.assertEqual(det["classification"], "APPROXIMATE")

        # Whole Egg ING0028 ~ 60g
        det = UnitConverter.convert_detailed(4.0, "piece", "g", ingredient_id="ING0028")
        self.assertAlmostEqual(det["converted_quantity"], 240.0, places=2)
        self.assertEqual(det["classification"], "APPROXIMATE")
        self.assertEqual(det["estimated_variance_pct"], 10.0)

    def test_density_liquid_approximate(self):
        # g to ml liquid density
        det = UnitConverter.convert_detailed(150.0, "g", "ml")
        self.assertEqual(det["converted_quantity"], 150.0)
        self.assertEqual(det["classification"], "APPROXIMATE")
        self.assertEqual(det["estimated_variance_pct"], 8.0)

    def test_unsupported_conversions(self):
        # Incompatible arbitrary units
        det = UnitConverter.convert_detailed(10.0, "cup", "car")
        self.assertIsNone(det["converted_quantity"])
        self.assertEqual(det["classification"], "UNSUPPORTED")
        self.assertFalse(det["is_supported"])

        # Undefined unit
        det2 = UnitConverter.convert_detailed(5.0, "pinch", "kg")
        self.assertIsNone(det2["converted_quantity"])
        self.assertEqual(det2["classification"], "UNSUPPORTED")

        # Mass to piece for non-produce (Salt cannot be converted to pieces)
        det3 = UnitConverter.convert_detailed(100.0, "g", "piece", ingredient_id="ING0057")
        self.assertIsNone(det3["converted_quantity"])
        self.assertEqual(det3["classification"], "UNSUPPORTED")


class TestCostCalculator(unittest.TestCase):
    """Test empirical recipe cost calculation against silla_staging.db."""

    def setUp(self):
        self.calculator = CostCalculator(db_path=STAGING_DB_PATH)

    def test_procurement_always_covers_required_quantity(self):
        """Audit guarantee: Grocery procurement packages must cover 100% of required quantity."""
        for rid in ["R0001", "R0002", "R0004", "R0007"]:
            res = self.calculator.calculate_recipe_cost(rid)
            self.assertTrue(res["success"])
            for item in res["priced_ingredients"]:
                pkg_size = item["matched_product"]["package_size"]
                pkgs = item["packages_needed"]
                needed = item["converted_quantity"]
                total_provided = pkgs * pkg_size
                self.assertGreaterEqual(
                    total_provided,
                    needed - 1e-6,
                    f"Procurement failed to cover needed qty for {item['ingredient_id']} in {rid}"
                )
                self.assertGreaterEqual(item["procurement_cost_egp"], item["pro_rata_cost_egp"])

    def test_coverage_depends_on_required_ingredients_not_products(self):
        """Audit guarantee: Coverage is N_priced / N_total required ingredients, not product count."""
        res = self.calculator.calculate_recipe_cost("R0001")
        self.assertEqual(res["total_ingredients_count"], 12)
        self.assertEqual(res["priced_ingredients_count"], 8)
        self.assertEqual(res["unpriced_ingredients_count"], 4)
        expected_coverage = 8.0 / 12.0
        self.assertAlmostEqual(res["price_completeness_ratio"], expected_coverage, places=4)

    def test_macaroni_bechamel_cost_recomputation(self):
        res = self.calculator.calculate_recipe_cost("R0001")
        self.assertTrue(res["success"])
        self.assertEqual(res["recipe_id"], "R0001")
        self.assertEqual(res["base_servings"], 6.0)

        # Net and procurement empirical costs
        self.assertEqual(res["net_recipe_cost_egp"], 185.12)
        self.assertEqual(res["grocery_procurement_cost_egp"], 452.00)
        self.assertEqual(res["net_cost_per_serving_egp"], 30.85)
        self.assertEqual(res["procurement_cost_per_serving_egp"], 75.33)

        # Check line item classifications
        classifications = {it["ingredient_id"]: it["conversion_classification"] for it in res["priced_ingredients"]}
        self.assertEqual(classifications["ING0052"], "EXACT")        # g to g
        self.assertEqual(classifications["ING0042"], "EXACT")        # g to g
        self.assertEqual(classifications["ING0071"], "APPROXIMATE")  # piece to g
        self.assertEqual(classifications["ING0062"], "APPROXIMATE")  # tbsp to g

        # Unpriced items transparent reporting
        unpriced_ids = [u["ingredient_id"] for u in res["unpriced_ingredients"]]
        self.assertIn("ING0070", unpriced_ids)  # Whole milk
        self.assertIn("ING0057", unpriced_ids)  # Salt
        self.assertIn("ING0048", unpriced_ids)  # Nutmeg
        self.assertIn("ING0065", unpriced_ids)  # Vegetable oil

    def test_kofta_cost_recomputation(self):
        res = self.calculator.calculate_recipe_cost("R0007")
        self.assertTrue(res["success"])
        self.assertEqual(res["net_recipe_cost_egp"], 213.80)
        self.assertEqual(res["grocery_procurement_cost_egp"], 348.50)
        self.assertEqual(res["base_servings"], 4.0)
        self.assertEqual(res["net_cost_per_serving_egp"], 53.45)
        self.assertEqual(res["procurement_cost_per_serving_egp"], 87.12)
        self.assertEqual(res["total_ingredients_count"], 8)
        self.assertEqual(res["priced_ingredients_count"], 6)

    def test_koshari_cost_recomputation(self):
        res = self.calculator.calculate_recipe_cost("R0002")
        self.assertTrue(res["success"])
        self.assertEqual(res["net_recipe_cost_egp"], 56.58)
        self.assertEqual(res["grocery_procurement_cost_egp"], 358.00)
        self.assertEqual(res["total_ingredients_count"], 14)
        self.assertEqual(res["priced_ingredients_count"], 7)
        self.assertEqual(res["price_completeness_ratio"], 0.5000)

    def test_mahshi_cost_recomputation(self):
        res = self.calculator.calculate_recipe_cost("R0004")
        self.assertTrue(res["success"])
        self.assertEqual(res["net_recipe_cost_egp"], 84.48)
        self.assertEqual(res["grocery_procurement_cost_egp"], 501.00)
        self.assertEqual(res["total_ingredients_count"], 14)
        self.assertEqual(res["priced_ingredients_count"], 9)
        self.assertAlmostEqual(res["price_completeness_ratio"], 9.0 / 14.0, places=4)

    def test_invalid_recipe_id(self):
        res = self.calculator.calculate_recipe_cost("R9999")
        self.assertFalse(res["success"])
        self.assertIn("error", res)

    def test_store_filtering(self):
        res_carrefour = self.calculator.calculate_recipe_cost("R0001", store_id="STR001")
        self.assertTrue(res_carrefour["success"])
        for item in res_carrefour["priced_ingredients"]:
            self.assertEqual(item["matched_product"]["store_id"], "STR001")


if __name__ == "__main__":
    unittest.main()
