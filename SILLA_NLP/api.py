"""
SILLA_NLP/api.py
================
Standard Public Integration Interface for SILLA Recipe Discovery & Matching Module.

Provides a production-ready, ergonomic API for downstream modules (Backend, Recommender, UI):
- match_recipe(query, language=None, top_k=3, threshold=None)
- SillaRecipeMatcher (Reusable singleton engine instance)

Output Schema:
{
    "status": "SUCCESS" | "REJECTED_OUT_OF_DOMAIN" | "REJECTED_OUT_OF_CATALOG" | "REQUEST_CLARIFICATION" | "LOW_CONFIDENCE",
    "query": str,
    "normalized_query": str,
    "language": "ar" | "en" | "mixed",
    "matched_recipes": [
        {
            "recipe_id": str,
            "recipe_name_ar": str,
            "recipe_name_en": str,
            "cuisine": str,
            "category": str,
            "similarity_score": float,
            "match_reason": str,
            "is_core_recipe": bool,
            "description_ar": str,
            "description_en": str
        }
    ],
    "rejection_reason": str | None,
    "rejection_reason_en": str | None,
    "clarification_message": str | None,
    "execution_time_ms": float
}
"""

import time
from pathlib import Path
from typing import Dict, List, Any, Optional

from SILLA_NLP.config.settings import STAGING_DB_PATH, REJECTION_THRESHOLD
from SILLA_NLP.matching.hybrid_engine import HybridEngine
from SILLA_NLP.preprocessing.query_preprocessor import preprocess_query_bundle


class SillaRecipeMatcher:
    """
    Unified Recipe Discovery Engine Service.
    Maintains pre-warmed embeddings and indexes in memory for low-latency retrieval.
    """

    _instance: Optional["SillaRecipeMatcher"] = None

    def __init__(self, db_path: Path = STAGING_DB_PATH, default_threshold: float = REJECTION_THRESHOLD):
        self.db_path = Path(db_path)
        self.default_threshold = default_threshold
        self.engine = HybridEngine(db_path=self.db_path, rejection_threshold=self.default_threshold)

    @classmethod
    def get_instance(cls, db_path: Path = STAGING_DB_PATH) -> "SillaRecipeMatcher":
        """Singleton accessor to prevent redundant model reloads."""
        if cls._instance is None:
            cls._instance = cls(db_path=db_path)
        return cls._instance

    def match(
        self,
        user_query: str,
        language: Optional[str] = None,
        top_k: int = 3,
        threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Match user query against SILLA recipes catalog.

        Args:
            user_query (str): The raw user search query (Arabic, Colloquial Egyptian, or English).
            language (str, optional): Language hint ('ar', 'en'). Defaults to auto-detect.
            top_k (int): Number of recipe candidates to return (default: 3).
            threshold (float, optional): Custom score threshold override.

        Returns:
            Dict[str, Any]: Standardized response dictionary.
        """
        t0 = time.time()
        tau = threshold if threshold is not None else self.default_threshold

        # Preprocess and language hint
        bundle = preprocess_query_bundle(user_query)
        detected_lang = language or bundle["language_hint"]

        # Run Search Pipeline
        raw_res = self.engine.search(user_query, top_k=top_k, threshold=tau)
        latency_ms = (time.time() - t0) * 1000.0

        status = raw_res["status"]
        guard_decision = raw_res.get("guard_decision", "N/A")

        # Map internal status to clean integration status
        if status == "SUCCESS":
            api_status = "SUCCESS"
            rejection_ar = None
            rejection_en = None
            clarification = None
        elif guard_decision == "REJECT_NON_FOOD":
            api_status = "REJECTED_OUT_OF_DOMAIN"
            rejection_ar = raw_res.get("rejection_reason_ar")
            rejection_en = raw_res.get("rejection_reason_en")
            clarification = None
        elif guard_decision == "REJECT_OUT_OF_CATALOG":
            api_status = "REJECTED_OUT_OF_CATALOG"
            rejection_ar = raw_res.get("rejection_reason_ar")
            rejection_en = raw_res.get("rejection_reason_en")
            clarification = None
        elif guard_decision == "REJECT_CONTRADICTORY":
            api_status = "REJECTED_CONTRADICTORY"
            rejection_ar = raw_res.get("rejection_reason_ar")
            rejection_en = raw_res.get("rejection_reason_en")
            clarification = "الطلب يحتوي على مكونات متعارضة جوهرياً. هل تبحث عن الوصفة التقليدية أم وصفة أخرى؟"
        elif guard_decision == "REQUEST_CLARIFICATION" or status == "REQUEST_CLARIFICATION":
            api_status = "REQUEST_CLARIFICATION"
            rejection_ar = None
            rejection_en = None
            clarification = raw_res.get("rejection_reason_ar", "الطلب غير محدد بدرجة كافية، يرجى كتابة اسم مكون أو أكلة معينة.")
        else:
            api_status = "LOW_CONFIDENCE"
            rejection_ar = raw_res.get("rejection_reason_ar", "لم يتم العثور على وصفة مطابقة بدرجة ثقة كافية.")
            rejection_en = raw_res.get("rejection_reason_en", "No recipe match exceeded the confidence threshold.")
            clarification = None

        # Build clean recipe candidate representations
        matched_recipes = []
        for r in raw_res.get("results", []):
            matched_recipes.append({
                "recipe_id": r["recipe_id"],
                "recipe_name_ar": r["recipe_name_ar"],
                "recipe_name_en": r["recipe_name_en"],
                "cuisine": r["cuisine"],
                "category": r["category"],
                "similarity_score": round(float(r["hybrid_score"]), 4),
                "match_reason": r["match_rationale"],
                "is_core_recipe": bool(r["is_core"]),
                "description_ar": r["description_ar"],
                "description_en": r["description_en"]
            })

        return {
            "status": api_status,
            "query": user_query,
            "normalized_query": bundle["normalized_query"],
            "language": detected_lang,
            "matched_recipes": matched_recipes,
            "rejection_reason": rejection_ar,
            "rejection_reason_en": rejection_en,
            "clarification_message": clarification,
            "execution_time_ms": round(latency_ms, 2)
        }


# Module-level convenience function
def match_recipe(
    query: str,
    language: Optional[str] = None,
    top_k: int = 3,
    threshold: Optional[float] = None
) -> Dict[str, Any]:
    """
    Convenience functional API for single-call recipe discovery.
    Uses cached singleton matcher instance.
    """
    matcher = SillaRecipeMatcher.get_instance()
    return matcher.match(user_query=query, language=language, top_k=top_k, threshold=threshold)
