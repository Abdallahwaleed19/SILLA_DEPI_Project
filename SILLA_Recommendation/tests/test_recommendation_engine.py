"""
SILLA_Recommendation/tests/test_recommendation_engine.py
========================================================
Automated unit tests for RecommendationEngine:
- Query intent guarding & rejection suppression.
- Positive recipe recommendation ranking.
- Cost & availability integration.
- Intent dominance over product availability.
- CoreBoost impact verification.
"""

import unittest
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from SILLA_Recommendation.config import STAGING_DB_PATH, CORE_EGYPTIAN_RECIPE_IDS
from SILLA_Recommendation.recommendation_engine import RecommendationEngine


class TestRecommendationEngine(unittest.TestCase):
    """Test recommendation engine integration with NLP, Cost Calculator, and Guard Suppression."""

    @classmethod
    def setUpClass(cls):
        cls.engine = RecommendationEngine(db_path=STAGING_DB_PATH)

    def test_positive_macaroni_bechamel(self):
        res = self.engine.recommend("مكرونة بشاميل", top_k=3)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertFalse(res["guard_triggered"])
        self.assertGreater(res["total_recommendations"], 0)
        top1 = res["recommendations"][0]
        self.assertEqual(top1["recipe_id"], "R0001")
        self.assertEqual(top1["recipe_name_ar"], "مكرونة بشاميل")
        self.assertGreater(top1["recommendation_score"], 0.0)
        self.assertGreater(top1["net_recipe_cost_egp"], 0.0)
        self.assertIn("FEASIBILITY", top1["feasibility_tier"])

    def test_positive_kofta(self):
        res = self.engine.recommend("كفتة مشوية على الفحم", top_k=3)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertFalse(res["guard_triggered"])
        self.assertGreater(res["total_recommendations"], 0)
        top1 = res["recommendations"][0]
        self.assertEqual(top1["recipe_id"], "R0007")

    def test_positive_koshari(self):
        res = self.engine.recommend("عايز كشري مصري", top_k=3)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertFalse(res["guard_triggered"])
        top1 = res["recommendations"][0]
        self.assertEqual(top1["recipe_id"], "R0002")

    def test_english_query(self):
        res = self.engine.recommend("Egyptian Koshari", language="en", top_k=3)
        self.assertEqual(res["status"], "SUCCESS")
        top1 = res["recommendations"][0]
        self.assertEqual(top1["recipe_id"], "R0002")

    def test_intent_dominance_over_coverage(self):
        """Audit guarantee: Closest recipe does NOT lose rank merely because another has higher coverage."""
        # For 'Egyptian Koshari', Koshari (R0002) has 50% coverage, Shakshuka (R0009) has 81.8% coverage.
        # Koshari MUST remain #1.
        res = self.engine.recommend("Egyptian Koshari", language="en", top_k=3)
        self.assertEqual(res["recommendations"][0]["recipe_id"], "R0002")

        # For 'كفتة مشوية', Kofta (R0007) has 75% coverage, competitor lentil dish has 83.3% coverage.
        # Kofta MUST remain #1.
        res_kofta = self.engine.recommend("كفتة مشوية", top_k=3)
        self.assertEqual(res_kofta["recommendations"][0]["recipe_id"], "R0007")

    def test_core_boost_impact(self):
        """Audit guarantee: Core authentic recipes (R0001-R0016) receive documented +0.05 boost."""
        res = self.engine.recommend("مكرونة بشاميل", top_k=3)
        top1 = res["recommendations"][0]
        self.assertIn(top1["recipe_id"], CORE_EGYPTIAN_RECIPE_IDS)
        # Verify recommendation score contains core boost
        nlp_s = top1["nlp_similarity_score"]
        cov = top1["ingredient_coverage_ratio"]
        expected_score = round((nlp_s * (0.70 + 0.30 * cov)) + 0.05, 4)
        self.assertAlmostEqual(top1["recommendation_score"], expected_score, places=4)

    def test_top_k_parameter(self):
        res = self.engine.recommend("مكرونة", top_k=2)
        self.assertEqual(res["status"], "SUCCESS")
        self.assertLessEqual(len(res["recommendations"]), 2)

    def test_suppress_out_of_domain_query(self):
        res = self.engine.recommend("عايز شاحن ايفون سريع")
        self.assertEqual(res["status"], "REJECTED_OUT_OF_DOMAIN")
        self.assertTrue(res["guard_triggered"])
        self.assertEqual(res["total_recommendations"], 0)
        self.assertEqual(len(res["recommendations"]), 0)

    def test_suppress_out_of_catalog_query(self):
        res = self.engine.recommend("حلويات شرقية بسبوسة بالقشطة")
        self.assertEqual(res["status"], "REJECTED_OUT_OF_CATALOG")
        self.assertTrue(res["guard_triggered"])
        self.assertEqual(res["total_recommendations"], 0)
        self.assertEqual(len(res["recommendations"]), 0)

    def test_suppress_contradictory_query(self):
        res = self.engine.recommend("كشري بالسمك والجمبري")
        self.assertEqual(res["status"], "REJECTED_CONTRADICTORY")
        self.assertTrue(res["guard_triggered"])
        self.assertEqual(res["total_recommendations"], 0)
        self.assertEqual(len(res["recommendations"]), 0)

    def test_suppress_vague_query(self):
        res = self.engine.recommend("اكل")
        self.assertEqual(res["status"], "REQUEST_CLARIFICATION")
        self.assertTrue(res["guard_triggered"])
        self.assertEqual(res["total_recommendations"], 0)
        self.assertEqual(len(res["recommendations"]), 0)


if __name__ == "__main__":
    unittest.main()
