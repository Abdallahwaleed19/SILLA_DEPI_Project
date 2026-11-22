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
        """Verify 'ممكن وصفة سهلة بالدجاج والبطاطس' benefits from co-occurrence and ranks R0014 at top."""
        resp = match_recipe("ممكن وصفة سهلة بالدجاج والبطاطس", top_k=3)
        self.assertEqual(resp["status"], "SUCCESS")
        self.assertTrue(len(resp["matched_recipes"]) > 0)
        top = resp["matched_recipes"][0]
        self.assertEqual(top["recipe_id"], "R0014", f"Expected R0014 Egyptian Potato and Chicken Tray, got {top['recipe_id']} - {top['recipe_name_ar']}")
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
        self.assertIn(top["recipe_id"], ["R0007", "R0006", "R0001", "R0013", "R0015"])

    def test_english_chicken_and_potatoes(self):
        """Verify 'I want a quick meal with chicken and potatoes' returns R0014 at rank 1."""
        resp = match_recipe("I want a quick meal with chicken and potatoes", top_k=3)
        self.assertEqual(resp["status"], "SUCCESS")
        self.assertTrue(len(resp["matched_recipes"]) > 0)
        top = resp["matched_recipes"][0]
        self.assertEqual(top["recipe_id"], "R0014")

    def test_english_potatoes_and_tomatoes(self):
        """Verify 'Can you suggest a recipe with potatoes and tomatoes?' returns potato stew with tomatoes."""
        resp = match_recipe("Can you suggest a recipe with potatoes and tomatoes?", top_k=3)
        self.assertEqual(resp["status"], "SUCCESS")
        self.assertTrue(len(resp["matched_recipes"]) > 0)
        top = resp["matched_recipes"][0]
        self.assertIn(top["recipe_id"], ["R0164", "R0162", "R0171", "R0014"])

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
        """Verify Arabic and English pizza queries match in-catalog pizza recipes."""
        queries = ["عايز بيتزا مارجريتا", "طريقة عمل البيتزا في البيت", "pizza recipe", "Could you suggest a pizza recipe?"]
        for q in queries:
            resp = match_recipe(q, top_k=3)
            self.assertEqual(resp["status"], "SUCCESS", f"Query '{q}' should be accepted as in-catalog")
            self.assertTrue(len(resp["matched_recipes"]) > 0, f"Query '{q}' should return results")
            top_rec = resp["matched_recipes"][0]
            is_pizza = "بيتزا" in top_rec["recipe_name_ar"] or "pizza" in top_rec["recipe_name_en"].lower()
            self.assertTrue(is_pizza, f"Query '{q}' did not return a pizza recipe (got {top_rec['recipe_name_ar']})")
            self.assertIn(top_rec["recipe_id"], ["R0074", "R0231"])

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
        self.assertIn(resp2["matched_recipes"][0]["recipe_id"], ["R0185", "R0178"])
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
        for r in resp["matched_recipes"]:
            text = (r["recipe_name_ar"] + " " + r["recipe_name_en"]).lower()
            self.assertNotIn("جبن", text, f"Recipe {r['recipe_id']} has cheese in title!")
            self.assertNotIn("cheese", text, f"Recipe {r['recipe_id']} has cheese in title!")


    def test_priority_0_negation_expressions(self):
        """Verify Priority 0 negation expressions strictly exclude negated ingredients and request clarification if pure exclusion."""
        pure_negation_queries = [
            ("مش عايز حاجة فيها جبنة.", "جبنة"),
            ("مش عاوز فراخ.", "فراخ"),
            ("أريد وصفة لا تحتوي على اللحوم أو الدواجن.", "اللحوم"),
            ("وصفة لا تتضمن منتجات الألبان.", "الألبان"),
            ("مش حابب أكل فيه سمك.", "سمك")
        ]
        for q, excluded in pure_negation_queries:
            resp = match_recipe(q, top_k=3)
            self.assertEqual(resp["status"], "REQUEST_CLARIFICATION", f"Query '{q}' must request clarification")
            self.assertEqual(len(resp["matched_recipes"]), 0, f"Query '{q}' must return 0 recipes")
            self.assertIsNotNone(resp["clarification_message"])
            self.assertIn(excluded, resp["clarification_message"])

    def test_negation_with_positive_resumption(self):
        """Verify negation followed by a positive preference returns compliant recipes."""
        resp = match_recipe("مش حابب أكل فيه سمك، عايز فراخ.", top_k=3)
        self.assertEqual(resp["status"], "SUCCESS")
        self.assertTrue(len(resp["matched_recipes"]) > 0)
        prohibited = {"سمك", "fish", "جمبري", "seafood", "تونة", "تونه"}
        for r in resp["matched_recipes"]:
            combined = (r["recipe_name_ar"] + " " + r["recipe_name_en"]).lower()
            for p in prohibited:
                self.assertNotIn(p, combined, f"Found prohibited item '{p}' in recipe: {r['recipe_name_ar']}")
            self.assertTrue("دجاج" in r["recipe_name_ar"] or "فراخ" in r["recipe_name_ar"] or "Chicken" in r["recipe_name_en"])

    def test_priority_1_conversational_and_fillers(self):
        """Verify conversational fillers are stripped cleanly without polluting ingredient stems."""
        q1 = "ممكن أعمل إيه بالعدس اللي عندي؟"
        resp1 = match_recipe(q1, top_k=3)
        self.assertEqual(resp1["status"], "SUCCESS")
        self.assertTrue(len(resp1["matched_recipes"]) > 0)
        self.assertIn("عدس", resp1["matched_recipes"][0]["recipe_name_ar"])

        q2 = "اقترح وصفة تعتمد على العدس."
        resp2 = match_recipe(q2, top_k=3)
        self.assertEqual(resp2["status"], "SUCCESS")
        self.assertTrue(len(resp2["matched_recipes"]) > 0)
        self.assertIn("عدس", resp2["matched_recipes"][0]["recipe_name_ar"])

        q3 = "عندي رز وطماطم، أطبخ إيه؟"
        resp3 = match_recipe(q3, top_k=3)
        self.assertEqual(resp3["status"], "SUCCESS")
        self.assertTrue(len(resp3["matched_recipes"]) > 0)

    def test_priority_1_hunger_and_contextual_ambiguity(self):
        """Verify ambiguous hunger states and generic modifiers trigger clarification without guessing."""
        ambiguous_queries = [
            "أنا جعان وعايز أكلة سريعة.",
            "عايز أكلة خفيفة ومش تقيلة.",
            "أكلة حلوة كده وسهلة."
        ]
        for q in ambiguous_queries:
            resp = match_recipe(q, top_k=3)
            self.assertEqual(resp["status"], "REQUEST_CLARIFICATION", f"Query '{q}' should trigger clarification")
            self.assertEqual(len(resp["matched_recipes"]), 0)

    def test_simulation_colloquial_fillers_and_prefixes(self):
        """Verify colloquial Egyptian prefixes (بص يا سيدي, معنديش غير, لو سمحت, في التلاجة)."""
        # Q16: بص يا سيدي، عندي عدس وطماطم
        r16 = match_recipe("بص يا سيدي، عندي عدس وطماطم، أعمل بيهم إيه؟", top_k=3)
        self.assertEqual(r16["status"], "SUCCESS")
        self.assertTrue(len(r16["matched_recipes"]) > 0)
        self.assertTrue(any("عدس" in r["recipe_name_ar"] or "طماطم" in r["recipe_name_ar"] for r in r16["matched_recipes"]))

        # Q18: أنا معنديش غير رز وبصل
        r18 = match_recipe("أنا معنديش غير رز وبصل، ينفع أعمل إيه؟", top_k=3)
        self.assertEqual(r18["status"], "SUCCESS")
        self.assertTrue(len(r18["matched_recipes"]) > 0)

        # Q19: لو سمحت عايز وصفة للفراخ تكون حلوة
        r19 = match_recipe("لو سمحت عايز وصفة للفراخ تكون حلوة.", top_k=3)
        self.assertEqual(r19["status"], "SUCCESS")
        self.assertTrue("دجاج" in r19["matched_recipes"][0]["recipe_name_ar"] or "فراخ" in r19["matched_recipes"][0]["recipe_name_ar"])

        # Q22: عندي شوية خضار في التلاجة
        r22 = match_recipe("عندي شوية خضار في التلاجة، أستفيد بيهم إزاي؟", top_k=3)
        self.assertEqual(r22["status"], "SUCCESS")
        self.assertTrue(len(r22["matched_recipes"]) > 0)

    def test_simulation_negation_and_exclusions(self):
        """Verify strict exclusion of onion, spicy, animal products, and fish with positive resumption."""
        import sqlite3
        conn = sqlite3.connect(PROJECT_ROOT / "SILLA_Data_Engineering/database/silla_staging.db")
        cur = conn.cursor()

        def _get_recipe_ingredients(rid):
            cur.execute("""
                SELECT i.canonical_name_en, i.canonical_name_ar, ri.original_ingredient_name
                FROM recipe_ingredients ri
                LEFT JOIN ingredients i ON ri.ingredient_id = i.ingredient_id
                WHERE ri.recipe_id = ?
            """, (rid,))
            return [(r[0] or r[2], r[1] or '') for r in cur.fetchall()]

        # Q62: I want chicken but no onions
        r62 = match_recipe("I want chicken but no onions.", top_k=3)
        self.assertEqual(r62["status"], "SUCCESS")
        top_62 = r62["matched_recipes"][0]
        self.assertTrue("دجاج" in top_62["recipe_name_ar"] or "Chicken" in top_62["recipe_name_en"])
        ings_62 = _get_recipe_ingredients(top_62["recipe_id"])
        c_62 = " ".join([f"{i[0]} {i[1]}" for i in ings_62]).lower()
        self.assertNotIn("onion", c_62)
        self.assertNotIn("بصل", c_62)

        # Q64: مش عايز سمك، ممكن فراخ؟
        r64 = match_recipe("مش عايز سمك، ممكن فراخ؟", top_k=3)
        self.assertEqual(r64["status"], "SUCCESS")
        top_64 = r64["matched_recipes"][0]
        self.assertTrue("دجاج" in top_64["recipe_name_ar"] or "Chicken" in top_64["recipe_name_en"])
        ings_64 = _get_recipe_ingredients(top_64["recipe_id"])
        c_64 = " ".join([f"{i[0]} {i[1]}" for i in ings_64]).lower()
        self.assertNotIn("fish", c_64)
        self.assertNotIn("سمك", c_64)

        # Q65: عايز أكلة نباتية تمامًا من غير أي منتجات حيوانية
        r65 = match_recipe("عايز أكلة نباتية تمامًا من غير أي منتجات حيوانية.", top_k=3)
        self.assertEqual(r65["status"], "SUCCESS")
        top_65 = r65["matched_recipes"][0]
        ings_65 = _get_recipe_ingredients(top_65["recipe_id"])
        c_65 = " ".join([f"{i[0]} {i[1]}" for i in ings_65]).lower()
        for forbidden in ["meat", "beef", "chicken", "poultry", "fish", "لحم", "دجاج", "سمك"]:
            self.assertNotIn(forbidden, c_65)

        # Q83: عايز حاجة مش حارة -> Pure exclusion without alternative -> Clarification
        r83 = match_recipe("عايز حاجة مش حارة.", top_k=3)
        self.assertEqual(r83["status"], "REQUEST_CLARIFICATION")
        self.assertEqual(len(r83["matched_recipes"]), 0)

        # Positive alternative with non-spicy: عايز فراخ مش حارة -> Non-spicy chicken
        r_spicy_alt = match_recipe("عايز فراخ مش حارة.", top_k=3)
        self.assertEqual(r_spicy_alt["status"], "SUCCESS")
        self.assertNotEqual(r_spicy_alt["matched_recipes"][0]["recipe_id"], "R0185", "Spicy pigeon must never be returned for non-spicy request!")

        # Q33: أبحث عن وصفة لا تحتوي على منتجات الألبان -> Pure dairy exclusion -> Clarification
        r33 = match_recipe("أبحث عن وصفة لا تحتوي على منتجات الألبان.", top_k=3)
        self.assertEqual(r33["status"], "REQUEST_CLARIFICATION")
        self.assertEqual(len(r33["matched_recipes"]), 0)

        conn.close()

    def test_simulation_ambiguity_and_modifiers(self):
        """Verify abstract economic, hunger, and idea queries trigger clarification."""
        queries = [
            "اقترح وجبة اقتصادية بمكونات بسيطة.",
            "I'm hungry. What should I cook?",
            "I want something quick and affordable.",
            "Give me an easy homemade dinner idea.",
            "ممكن recipe تكون healthy ورخيصة؟",
            "نفسي في حاجة خفيفة ومش دسمة."
        ]
        for q in queries:
            resp = match_recipe(q, top_k=3)
            self.assertEqual(resp["status"], "REQUEST_CLARIFICATION", f"Expected REQUEST_CLARIFICATION for '{q}', got {resp['status']}")
            self.assertEqual(len(resp["matched_recipes"]), 0, f"Expected 0 recipes for '{q}'")


if __name__ == "__main__":
    unittest.main()
