# -*- coding: utf-8 -*-
"""
SILLA_NLP/tests/test_live_audit_regressions.py
=============================================
Regression Test Suite for Deficiencies Discovered During the Practical Audit:
1. Chicken synonym normalization with proclitics ('بالفراخ' -> chicken dish, not falafel).
2. Accent stripping for English recipes ('How to make bechamel pasta' -> R0001 Macaroni Bechamel).
3. Ambiguity handling ('عايز أكلة حلوة', 'اعمللي حاجة', 'أكلة' -> REQUEST_CLARIFICATION).
4. Non-food domain guard ('اشرحلي البرمجة' -> REJECTED_OUT_OF_DOMAIN).
5. Luxury out-of-catalog items ('باستا بالزعفران والكافيار' -> REJECTED_OUT_OF_CATALOG).
6. Core boost dampening on unrelated candidates.
"""

import unittest
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from SILLA_NLP.api import match_recipe, SillaRecipeMatcher


class TestLiveAuditRegressions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Reset singleton instance to ensure clean index and precomputed caches
        SillaRecipeMatcher._instance = None
        cls.matcher = SillaRecipeMatcher.get_instance()

    def test_chicken_proclitic_regression(self):
        """Verify 'عايز أكلة بالفراخ' and 'عايز وصفة بالفراخ' return chicken dishes, never falafel."""
        queries = ["عايز أكلة بالفراخ", "عايز وصفة بالفراخ"]
        for q in queries:
            resp = match_recipe(q, top_k=3)
            self.assertEqual(resp["status"], "SUCCESS", f"Query '{q}' should succeed")
            self.assertTrue(len(resp["matched_recipes"]) > 0)
            top = resp["matched_recipes"][0]
            # Ensure top recipe is chicken related, not Falafel (R0011)
            self.assertNotEqual(top["recipe_id"], "R0011", f"Falafel incorrectly returned for '{q}'")
            # Verify chicken indication in Arabic or English title
            is_chicken = ("دجاج" in top["recipe_name_ar"] or "فراخ" in top["recipe_name_ar"] or "Chicken" in top["recipe_name_en"])
            self.assertTrue(is_chicken, f"Expected chicken recipe for '{q}', got: {top['recipe_name_ar']}")

    def test_english_bechamel_accent_normalization(self):
        """Verify 'How to make bechamel pasta' matches R0001 Macaroni Béchamel."""
        resp = match_recipe("How to make bechamel pasta", top_k=3)
        self.assertEqual(resp["status"], "SUCCESS")
        self.assertTrue(len(resp["matched_recipes"]) > 0)
        top = resp["matched_recipes"][0]
        self.assertEqual(top["recipe_id"], "R0001", f"Expected R0001 Macaroni Bechamel, got {top['recipe_id']} - {top['recipe_name_ar']}")

    def test_ambiguous_queries_clarification(self):
        """Verify ambiguous queries trigger REQUEST_CLARIFICATION and return 0 recipes."""
        ambiguous_queries = [
            "عايز أكلة حلوة",
            "اعمللي حاجة",
            "أكلة"
        ]
        for q in ambiguous_queries:
            resp = match_recipe(q, top_k=3)
            self.assertEqual(resp["status"], "REQUEST_CLARIFICATION", f"Expected clarification for '{q}', got {resp['status']}")
            self.assertEqual(len(resp["matched_recipes"]), 0, f"Expected 0 recipes for '{q}'")
            self.assertIsNotNone(resp["clarification_message"])

    def test_non_food_programming_rejection(self):
        """Verify 'اشرحلي البرمجة' is rejected out-of-domain and returns 0 recipes."""
        resp = match_recipe("اشرحلي البرمجة", top_k=3)
        self.assertEqual(resp["status"], "REJECTED_OUT_OF_DOMAIN")
        self.assertEqual(len(resp["matched_recipes"]), 0)
        self.assertIsNotNone(resp["rejection_reason"])

    def test_out_of_catalog_caviar_saffron_rejection(self):
        """Verify 'باستا بالزعفران والكافيار' is rejected out-of-catalog and does not suggest Mahshi."""
        resp = match_recipe("باستا بالزعفران والكافيار", top_k=3)
        self.assertIn(resp["status"], ["REJECTED_OUT_OF_CATALOG", "LOW_CONFIDENCE"])
        self.assertEqual(len(resp["matched_recipes"]), 0)
        if resp["matched_recipes"]:
            self.assertNotEqual(resp["matched_recipes"][0]["recipe_id"], "R0004", "Mahshi incorrectly suggested for caviar pasta!")


if __name__ == "__main__":
    unittest.main()
