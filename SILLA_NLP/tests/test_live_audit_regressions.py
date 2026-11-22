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

    def test_sweet_and_fast_clarification_no_savory(self):
        """Verify 'عايز حاجة حلوة وسريعة' with coordinating waw triggers REQUEST_CLARIFICATION without savory dishes."""
        resp = match_recipe("عايز حاجة حلوة وسريعة", top_k=3)
        self.assertEqual(resp["status"], "REQUEST_CLARIFICATION", f"Expected REQUEST_CLARIFICATION, got {resp['status']}")
        self.assertEqual(len(resp["matched_recipes"]), 0, "Ambiguous request must return 0 recipe candidates")
        self.assertIsNotNone(resp["clarification_message"])

    def test_chicken_and_potato_co_occurrence(self):
        """Verify 'ممكن وصفة سهلة بالدجاج والبطاطس' benefits from co-occurrence and ranks R0015 at top."""
        resp = match_recipe("ممكن وصفة سهلة بالدجاج والبطاطس", top_k=3)
        self.assertEqual(resp["status"], "SUCCESS")
        self.assertTrue(len(resp["matched_recipes"]) > 0)
        top = resp["matched_recipes"][0]
        self.assertEqual(top["recipe_id"], "R0015", f"Expected R0015 Classic Chicken Curry with potatoes, got {top['recipe_id']} - {top['recipe_name_ar']}")
        self.assertIn("بطاطس", top["match_reason"])
        self.assertIn("دجاج", top["match_reason"])

    def test_negation_without_alternative_arabic(self):
        """Verify 'عايز حاجة من غير لحمة' returns REQUEST_CLARIFICATION with 0 recipes."""
        queries = ["عايز حاجة من غير لحمة", "وصفة بدون فراخ", "أكلة خالية من السمك"]
        for q in queries:
            resp = match_recipe(q, top_k=3)
            self.assertEqual(resp["status"], "REQUEST_CLARIFICATION", f"Expected clarification for '{q}', got {resp['status']}")
            self.assertEqual(len(resp["matched_recipes"]), 0, f"Expected 0 recipes for '{q}'")
            self.assertIsNotNone(resp["clarification_message"])

    def test_negation_without_alternative_english(self):
        """Verify 'I want a recipe without meat' returns REQUEST_CLARIFICATION in English."""
        resp = match_recipe("I want a recipe without meat", top_k=3)
        self.assertEqual(resp["status"], "REQUEST_CLARIFICATION")
        self.assertEqual(len(resp["matched_recipes"]), 0)
        self.assertIsNotNone(resp["clarification_message"])

    def test_negation_with_alternative_vegetables(self):
        """Verify 'عايز أكلة من غير لحمة بالخضار' returns vegetable dishes and strictly excludes meat."""
        resp = match_recipe("عايز أكلة من غير لحمة بالخضار", top_k=3)
        self.assertEqual(resp["status"], "SUCCESS")
        self.assertTrue(len(resp["matched_recipes"]) > 0)
        for r in resp["matched_recipes"]:
            self.assertNotIn("لحم", r["recipe_name_ar"])
            self.assertNotIn("لحم", r["description_ar"])

    def test_negation_with_alternative_lentils(self):
        """Verify 'وصفة بدون فراخ بالعدس' returns lentil dishes and strictly excludes chicken."""
        resp = match_recipe("وصفة بدون فراخ بالعدس", top_k=3)
        self.assertEqual(resp["status"], "SUCCESS")
        self.assertTrue(len(resp["matched_recipes"]) > 0)
        for r in resp["matched_recipes"]:
            self.assertNotIn("دجاج", r["recipe_name_ar"])
            self.assertNotIn("فراخ", r["recipe_name_ar"])
            self.assertNotIn("Chicken", r["recipe_name_en"])

    def test_compound_negation_meat_and_chicken(self):
        """Verify 'عايز أكلة من غير لحمة ولا فراخ' returns REQUEST_CLARIFICATION and 0 recipes."""
        resp = match_recipe("عايز أكلة من غير لحمة ولا فراخ", top_k=3)
        self.assertEqual(resp["status"], "REQUEST_CLARIFICATION")
        self.assertEqual(len(resp["matched_recipes"]), 0)
        self.assertIsNotNone(resp["clarification_message"])

    def test_negation_dairy_and_cheese(self):
        """Verify 'وصفة بدون لبن أو جبنة' returns REQUEST_CLARIFICATION and 0 recipes."""
        resp = match_recipe("وصفة بدون لبن أو جبنة", top_k=3)
        self.assertEqual(resp["status"], "REQUEST_CLARIFICATION")
        self.assertEqual(len(resp["matched_recipes"]), 0)
        self.assertIsNotNone(resp["clarification_message"])

    def test_vegetarian_no_meat(self):
        """Verify 'عايز أكلة نباتية من غير أي لحوم' strictly returns meat-free recipes."""
        resp = match_recipe("عايز أكلة نباتية من غير أي لحوم", top_k=3)
        self.assertEqual(resp["status"], "SUCCESS")
        self.assertTrue(len(resp["matched_recipes"]) > 0)
        for r in resp["matched_recipes"]:
            combined_text = f"{r['recipe_name_ar']} {r['recipe_name_en']} {r['description_ar']}"
            for m in ["لحم", "دجاج", "فراخ", "Beef", "Chicken", "بتلو", "ضان"]:
                self.assertNotIn(m, combined_text)

    def test_ground_beef_preference(self):
        """Verify 'نفسي في أكلة باللحمة المفرومة' returns authentic ground beef recipes."""
        resp = match_recipe("نفسي في أكلة باللحمة المفرومة", top_k=3)
        self.assertEqual(resp["status"], "SUCCESS")
        self.assertTrue(len(resp["matched_recipes"]) > 0)
        top = resp["matched_recipes"][0]
        self.assertIn(top["recipe_id"], ["R0007", "R0006", "R0001", "R0013"])

    def test_english_chicken_and_potatoes(self):
        """Verify 'I want a quick meal with chicken and potatoes' returns R0015 at rank 1."""
        resp = match_recipe("I want a quick meal with chicken and potatoes", top_k=3)
        self.assertEqual(resp["status"], "SUCCESS")
        self.assertTrue(len(resp["matched_recipes"]) > 0)
        top = resp["matched_recipes"][0]
        self.assertEqual(top["recipe_id"], "R0015")

    def test_english_potatoes_and_tomatoes(self):
        """Verify 'Can you suggest a recipe with potatoes and tomatoes?' returns potato stew with tomatoes."""
        resp = match_recipe("Can you suggest a recipe with potatoes and tomatoes?", top_k=3)
        self.assertEqual(resp["status"], "SUCCESS")
        self.assertTrue(len(resp["matched_recipes"]) > 0)
        top = resp["matched_recipes"][0]
        self.assertIn(top["recipe_id"], ["R0164", "R0162", "R0171"])

    def test_vehicles_non_food_rejection(self):
        """Verify 'عايز أشتري عربية' is rejected as out-of-domain non-food."""
        resp = match_recipe("عايز أشتري عربية", top_k=3)
        self.assertEqual(resp["status"], "REJECTED_OUT_OF_DOMAIN")
        self.assertEqual(len(resp["matched_recipes"]), 0)

    def test_ai_non_food_rejection(self):
        """Verify 'اشرحلي الذكاء الاصطناعي' is rejected as out-of-domain non-food."""
        resp = match_recipe("اشرحلي الذكاء الاصطناعي", top_k=3)
        self.assertEqual(resp["status"], "REJECTED_OUT_OF_DOMAIN")
        self.assertEqual(len(resp["matched_recipes"]), 0)

    def test_sweets_craving_rejection(self):
        """Verify 'نفسي في حاجة مسكرة' is rejected as out-of-catalog."""
        resp = match_recipe("نفسي في حاجة مسكرة", top_k=3)
        self.assertEqual(resp["status"], "REJECTED_OUT_OF_CATALOG")
        self.assertEqual(len(resp["matched_recipes"]), 0)

    def test_dinner_light_ambiguity_clarification(self):
        """Verify 'عايز حاجة خفيفة وسريعة للعشا' returns REQUEST_CLARIFICATION."""
        resp = match_recipe("عايز حاجة خفيفة وسريعة للعشا", top_k=3)
        self.assertEqual(resp["status"], "REQUEST_CLARIFICATION")
        self.assertEqual(len(resp["matched_recipes"]), 0)

    def test_pizza_in_catalog_match(self):
        """Verify Arabic and English pizza queries match in-catalog recipe R0014 Pizza Margherita."""
        queries = ["عايز بيتزا مارجريتا", "طريقة عمل البيتزا في البيت", "pizza recipe", "Could you suggest a pizza recipe?"]
        for q in queries:
            resp = match_recipe(q, top_k=3)
            self.assertEqual(resp["status"], "SUCCESS", f"Query '{q}' should be accepted as in-catalog")
            self.assertTrue(len(resp["matched_recipes"]) > 0, f"Query '{q}' should return results")
            self.assertEqual(resp["matched_recipes"][0]["recipe_id"], "R0014", f"Query '{q}' should return R0014 at rank 1")

    def test_english_modal_questions_clarification(self):
        """Verify English modal questions with ambiguous intents trigger clarification."""
        queries = [
            "Could you suggest something healthy and cheap?",
            "Would you give me something quick for dinner?",
            "Can you suggest something light for lunch?"
        ]
        for q in queries:
            resp = match_recipe(q, top_k=3)
            self.assertEqual(resp["status"], "REQUEST_CLARIFICATION", f"Query '{q}' should request clarification")
            self.assertEqual(len(resp["matched_recipes"]), 0)

    def test_english_modal_questions_specific(self):
        """Verify English modal questions with specific ingredients match recipes successfully."""
        resp1 = match_recipe("Could you suggest a recipe with potatoes and tomatoes?", top_k=3)
        self.assertEqual(resp1["status"], "SUCCESS")
        self.assertTrue(len(resp1["matched_recipes"]) > 0)

        resp2 = match_recipe("Would you suggest an Egyptian rice dish?", top_k=3)
        self.assertEqual(resp2["status"], "SUCCESS")
        self.assertTrue(len(resp2["matched_recipes"]) > 0)
        self.assertEqual(resp2["matched_recipes"][0]["recipe_id"], "R0185")
        self.assertIn("rice", resp2["matched_recipes"][0]["recipe_name_en"].lower())

    def test_english_vegetarian_strict_exclusion(self):
        """Verify 'Give me a vegetarian recipe without meat.' returns strictly vegetarian recipes with 0 poultry/seafood/meat."""
        resp = match_recipe("Give me a vegetarian recipe without meat.", top_k=3)
        self.assertEqual(resp["status"], "SUCCESS")
        self.assertTrue(len(resp["matched_recipes"]) > 0)
        prohibited = {"chicken", "دجاج", "فراخ", "meat", "لحم", "beef", "fish", "سمك", "calamari", "حبار", "shrimp", "جمبري"}
        for r in resp["matched_recipes"]:
            name = (r["recipe_name_ar"] + " " + r["recipe_name_en"]).lower()
            for p in prohibited:
                self.assertNotIn(p, name, f"Vegetarian query returned prohibited item '{p}' in recipe: {name}")

    def test_negation_without_alternative_with_directive(self):
        """Verify 'اقترح وصفة من غير لحمة ولا فراخ.' requests clarification and returns 0 recipes."""
        resp = match_recipe("اقترح وصفة من غير لحمة ولا فراخ.", top_k=3)
        self.assertEqual(resp["status"], "REQUEST_CLARIFICATION")
        self.assertEqual(len(resp["matched_recipes"]), 0)

    def test_fridge_query_rice_tomato_onion(self):
        """Verify 'عندي رز وطماطم وبصل، أقدر أعمل إيه؟' matches Mahshi or Koshari."""
        resp = match_recipe("عندي رز وطماطم وبصل، أقدر أعمل إيه؟", top_k=3)
        self.assertEqual(resp["status"], "SUCCESS")
        self.assertTrue(len(resp["matched_recipes"]) > 0)
        top_ids = [r["recipe_id"] for r in resp["matched_recipes"]]
        self.assertTrue(any(rid in top_ids for rid in ["R0002", "R0004"]), f"Expected R0002 or R0004, got {top_ids}")

    def test_fridge_query_lentils(self):
        """Verify 'عندي عدس، اقترح عليا أكلة مناسبة.' matches lentil dishes."""
        resp = match_recipe("عندي عدس، اقترح عليا أكلة مناسبة.", top_k=3)
        self.assertEqual(resp["status"], "SUCCESS")
        self.assertTrue(len(resp["matched_recipes"]) > 0)
        top = resp["matched_recipes"][0]
        self.assertIn("عدس", top["recipe_name_ar"])

    def test_novelty_and_sweets_ambiguity(self):
        """Verify novelty and ambiguous descriptor queries trigger clarification."""
        for q in ["نفسي في حاجة مختلفة.", "اقترح عليا أكلة حلوة."]:
            resp = match_recipe(q, top_k=3)
            self.assertEqual(resp["status"], "REQUEST_CLARIFICATION", f"Query '{q}' should trigger clarification")
            self.assertEqual(len(resp["matched_recipes"]), 0)

    def test_pasta_without_cheese_strict(self):
        """Verify 'عايز مكرونة من غير جبنة.' returns pasta without cheese."""
        resp = match_recipe("عايز مكرونة من غير جبنة.", top_k=3)
        self.assertEqual(resp["status"], "SUCCESS")
        self.assertTrue(len(resp["matched_recipes"]) > 0)
        prohibited_ids = {"R0012", "R0013", "R0014"}  # Recipes with parmesan/mozzarella
        for r in resp["matched_recipes"]:
            self.assertNotIn(r["recipe_id"], prohibited_ids, f"Recipe {r['recipe_id']} has cheese!")


if __name__ == "__main__":
    unittest.main()
