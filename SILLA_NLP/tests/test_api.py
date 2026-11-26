"""
SILLA_NLP/tests/test_api.py
===========================
Automated Unit Tests for SILLA Public Integration API (SILLA_NLP.api).
"""

import unittest
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from SILLA_NLP import match_recipe, SillaRecipeMatcher


class TestSillaPublicAPI(unittest.TestCase):

    def test_match_recipe_success(self):
        resp = match_recipe("كشري مصري", top_k=3)
        self.assertEqual(resp["status"], "SUCCESS")
        self.assertEqual(resp["query"], "كشري مصري")
        self.assertTrue(len(resp["matched_recipes"]) > 0)
        
        top = resp["matched_recipes"][0]
        self.assertEqual(top["recipe_id"], "R0002")
        self.assertIn("كشري", top["recipe_name_ar"])
        self.assertGreater(top["similarity_score"], 0.50)
        self.assertTrue(top["is_core_recipe"])
        self.assertIsNotNone(top["match_reason"])
        self.assertIsNone(resp["rejection_reason"])
        self.assertIsNone(resp["clarification_message"])
        self.assertGreater(resp["execution_time_ms"], 0.0)

    def test_match_recipe_colloquial(self):
        resp = match_recipe("عايز اعمل حواوشي في العيش البلدي", top_k=1)
        self.assertEqual(resp["status"], "SUCCESS")
        self.assertEqual(resp["matched_recipes"][0]["recipe_id"], "R0006")

    def test_match_recipe_out_of_domain(self):
        resp = match_recipe("شاحن سريع للموبايل تايب سي")
        self.assertEqual(resp["status"], "REJECTED_OUT_OF_DOMAIN")
        self.assertEqual(len(resp["matched_recipes"]), 0)
        self.assertIsNotNone(resp["rejection_reason"])
        self.assertIn("غير غذائية", resp["rejection_reason"])

    def test_match_recipe_out_of_catalog(self):
        resp = match_recipe("تشيز كيك شوكولاتة")
        self.assertEqual(resp["status"], "REJECTED_OUT_OF_CATALOG")
        self.assertEqual(len(resp["matched_recipes"]), 0)
        self.assertIsNotNone(resp["rejection_reason"])
        self.assertIn("غير متوفر", resp["rejection_reason"])

    def test_match_recipe_clarification(self):
        resp = match_recipe("أكل سريع وخلاص")
        self.assertEqual(resp["status"], "REQUEST_CLARIFICATION")
        self.assertEqual(len(resp["matched_recipes"]), 0)
        self.assertIsNotNone(resp["clarification_message"])

    def test_match_recipe_english(self):
        resp = match_recipe("pasta with chicken and cream", top_k=2)
        self.assertEqual(resp["status"], "SUCCESS")
        self.assertEqual(resp["language"], "en")
        self.assertIn(resp["matched_recipes"][0]["recipe_id"], ["R0195", "R0012"])

    def test_match_recipe_contradictory_koshari_fish(self):
        resp = match_recipe("كشري بالسمك")
        self.assertEqual(resp["status"], "REJECTED_CONTRADICTORY")
        self.assertEqual(len(resp["matched_recipes"]), 0)
        self.assertIn("تعارض جوهري", resp["rejection_reason"])
        self.assertIsNotNone(resp["clarification_message"])

    def test_match_recipe_contradictory_bechamel_jam(self):
        resp = match_recipe("مكرونة بشاميل بالمربى والشوكولاتة")
        self.assertEqual(resp["status"], "REJECTED_CONTRADICTORY")
        self.assertEqual(len(resp["matched_recipes"]), 0)
        self.assertIn("تعارض جوهري", resp["rejection_reason"])
        self.assertIsNotNone(resp["clarification_message"])

    def test_singleton_matcher(self):
        m1 = SillaRecipeMatcher.get_instance()
        m2 = SillaRecipeMatcher.get_instance()
        self.assertIs(m1, m2)


if __name__ == "__main__":
    unittest.main()
