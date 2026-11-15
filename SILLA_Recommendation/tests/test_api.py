"""
SILLA_Recommendation/tests/test_api.py
======================================
Automated unit tests for public API interface:
- get_recommendations
- calculate_recipe_cost
- build_smart_cart
"""

import unittest
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from SILLA_Recommendation.api import (
    get_recommendations,
    calculate_recipe_cost,
    build_smart_cart,
)


class TestAPIInterface(unittest.TestCase):
    """Test top-level convenience API functions."""

    def test_api_get_recommendations(self):
        res = get_recommendations("مكرونة بشاميل", top_k=2)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertLessEqual(len(res["recommendations"]), 2)
        self.assertEqual(res["recommendations"][0]["recipe_id"], "R0001")

    def test_api_calculate_recipe_cost(self):
        res = calculate_recipe_cost("R0001")
        self.assertTrue(res["success"])
        self.assertEqual(res["recipe_id"], "R0001")
        self.assertGreater(res["net_recipe_cost_egp"], 0.0)

    def test_api_build_smart_cart(self):
        res = build_smart_cart(["R0001", "R0007"])
        self.assertTrue(res["success"])
        self.assertGreater(res["total_savings_egp"], 0.0)
        self.assertEqual(len(res["recipes"]), 2)


if __name__ == "__main__":
    unittest.main()
