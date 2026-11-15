"""
SILLA_NLP/tests/test_hybrid_engine.py
=====================================
Automated Unit and Regression Test Suite for SILLA Hybrid NLP Engine.
"""

import unittest
from pathlib import Path

from SILLA_NLP.config.settings import STAGING_DB_PATH
from SILLA_NLP.preprocessing.query_preprocessor import (
    normalize_arabic,
    clean_query_text,
    preprocess_query_bundle,
    stem_arabic_token,
    extract_content_stems
)
from SILLA_NLP.intent_guard.domain_guard import DomainGuard
from SILLA_NLP.matching.sparse_engine import SparseEngine
from SILLA_NLP.matching.dense_engine import DenseEngine
from SILLA_NLP.matching.hybrid_engine import HybridEngine


class TestQueryPreprocessor(unittest.TestCase):
    def test_normalize_arabic_diacritics_and_tatweel(self):
        raw = "كُشَرِيّ مَصْـرِيّ"
        norm = normalize_arabic(raw)
        self.assertNotIn("َ", norm)
        self.assertNotIn("ّ", norm)
        self.assertNotIn("ـ", norm)
        self.assertIn("كشري", norm)

    def test_normalize_arabic_alef_variants(self):
        raw = "أرز أبيض إسكندراني آيس"
        norm = normalize_arabic(raw)
        self.assertTrue(norm.startswith("ارز ابيض"))

    def test_strip_conversational_prefixes(self):
        q1 = "عايز اعمل حواوشي"
        self.assertEqual(clean_query_text(q1), "حواوشي")

        q2 = "طريقة عمل مكرونة بشاميل"
        self.assertEqual(clean_query_text(q2), "مكرونة بشاميل")

        q3 = "how to make chicken curry"
        self.assertEqual(clean_query_text(q3), "chicken curry")

    def test_egyptian_synonym_normalization(self):
        q = "صينية فراخ بالقوطة والرز والعيش البلدي مع توم"
        cleaned = clean_query_text(q)
        self.assertIn("دجاج", cleaned)
        self.assertNotIn("فراخ", cleaned)
        self.assertIn("طماطم", cleaned)
        self.assertNotIn("قوطة", cleaned)
        self.assertIn("ارز", cleaned)
        self.assertNotIn(" رز ", f" {cleaned} ")
        self.assertIn("خبز بلدي", cleaned)
        self.assertIn("ثوم", cleaned)

    def test_light_arabic_stemming(self):
        self.assertEqual(stem_arabic_token("الكفتة"), "كفته")
        self.assertEqual(stem_arabic_token("المشوية"), "مشويه")
        self.assertEqual(stem_arabic_token("الفحم"), "فحم")
        self.assertEqual(stem_arabic_token("ارز"), "ارز")


class TestDomainGuard(unittest.TestCase):
    def setUp(self):
        self.guard = DomainGuard()

    def test_reject_non_food(self):
        queries = [
            "شاحن موبايل تايب سي سريع",
            "سماعات بلوتوث للكمبيوتر",
            "كابل شاحن ايفون",
            "laptop charger"
        ]
        for q in queries:
            res = self.guard.inspect(q, clean_query_text(q))
            self.assertFalse(res["is_valid"], f"Failed to reject: {q}")
            self.assertEqual(res["decision"], "REJECT_NON_FOOD")

    def test_reject_out_of_catalog_food(self):
        queries = [
            "سوشي ياباني سلمون",
            "تشيز كيك شوكولاتة",
            "ساندوتش برجر بيج ماك",
            "كنافة بالقشطة وحلويات"
        ]
        for q in queries:
            res = self.guard.inspect(q, clean_query_text(q))
            self.assertFalse(res["is_valid"], f"Failed to reject: {q}")
            self.assertEqual(res["decision"], "REJECT_OUT_OF_CATALOG")

    def test_request_clarification_on_ambiguous(self):
        queries = ["أكل", "طعام", "وجبة", "حاجة سريعة"]
        for q in queries:
            res = self.guard.inspect(q, clean_query_text(q))
            self.assertFalse(res["is_valid"], f"Failed to clarify: {q}")
            self.assertEqual(res["decision"], "REQUEST_CLARIFICATION")

    def test_accept_valid_food_queries(self):
        queries = [
            "كشري مصري",
            "مكرونة بشاميل باللحمة",
            "شوربة عدس بالشعرية",
            "Egyptian fattah with meat",
            "pasta with chicken and cream"
        ]
        for q in queries:
            res = self.guard.inspect(q, clean_query_text(q))
            self.assertTrue(res["is_valid"], f"Unexpectedly rejected valid query: {q}")
            self.assertEqual(res["decision"], "ACCEPT")


class TestSparseEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = SparseEngine(STAGING_DB_PATH)

    def test_corpus_size(self):
        self.assertEqual(len(self.engine.recipe_ids), 185)

    def test_exact_recipe_match(self):
        results = self.engine.search("كشري مصري", top_k=3)
        self.assertTrue(len(results) > 0)
        top_id, top_score = results[0]
        self.assertEqual(top_id, "R0002")
        self.assertGreater(top_score, 0.15)


class TestDenseEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = DenseEngine(STAGING_DB_PATH)

    def test_embeddings_dimensions(self):
        self.assertEqual(self.engine.embeddings.shape, (185, 384))

    def test_search_score_bounds(self):
        results = self.engine.search("pasta with chicken and cream", top_k=3)
        self.assertTrue(len(results) > 0)
        for rid, score in results:
            self.assertGreaterEqual(score, 0.0)
            self.assertLessEqual(score, 1.0)


class TestHybridEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.engine = HybridEngine(STAGING_DB_PATH)

    def test_in_catalog_koshari(self):
        resp = self.engine.search("كشري مصري", top_k=3)
        self.assertTrue(resp["is_valid"])
        self.assertEqual(resp["status"], "SUCCESS")
        self.assertEqual(resp["results"][0]["recipe_id"], "R0002")
        self.assertIn("تطابق في عنوان الوصفة", resp["results"][0]["match_rationale"])

    def test_colloquial_hawawshi(self):
        resp = self.engine.search("عايز اعمل حواوشي في العيش البلدي", top_k=3)
        self.assertTrue(resp["is_valid"])
        self.assertEqual(resp["results"][0]["recipe_id"], "R0006")

    def test_rejection_charger(self):
        resp = self.engine.search("شاحن موبايل تايب سي سريع", top_k=3)
        self.assertFalse(resp["is_valid"])
        self.assertEqual(resp["status"], "REJECTED_GUARD")
        self.assertEqual(len(resp["results"]), 0)

    def test_rejection_sushi(self):
        resp = self.engine.search("سوشي ياباني بالسالمون", top_k=3)
        self.assertFalse(resp["is_valid"])
        self.assertEqual(resp["status"], "REJECTED_GUARD")
        self.assertEqual(len(resp["results"]), 0)


if __name__ == "__main__":
    unittest.main()
