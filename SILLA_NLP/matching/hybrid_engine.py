"""
SILLA_NLP/matching/hybrid_engine.py
==================================
Unified Hybrid NLP Retrieval Engine combining Sparse TF-IDF and Dense Sentence Transformers.

Features:
- Full Integration of Query Preprocessing, Domain Guarding, and Egyptian Normalization.
- Balanced Score Fusion: alpha * Dense + (1 - alpha) * Sparse.
- Exact Title & Key Term Overlap Matching Bonus.
- Core Curated Recipe Prioritization (R0001-R0016) while preserving full catalog visibility.
- Comprehensive Match Rationale & Score Explainability.
- Strict Domain & Quality Rejection (Non-Food, Out-of-Catalog, Low-Confidence).
"""

import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

from SILLA_NLP.config.settings import (
    STAGING_DB_PATH,
    DEFAULT_DENSE_WEIGHT,
    DEFAULT_SPARSE_WEIGHT,
    CORE_RECIPE_BOOST,
    EXACT_TITLE_BONUS,
    REJECTION_THRESHOLD,
    AMBIGUITY_THRESHOLD
)
from SILLA_NLP.preprocessing.query_preprocessor import (
    preprocess_query_bundle,
    normalize_arabic,
    extract_content_stems
)
from SILLA_NLP.intent_guard.domain_guard import DomainGuard
from SILLA_NLP.matching.sparse_engine import SparseEngine
from SILLA_NLP.matching.dense_engine import DenseEngine

logger = logging.getLogger("SILLA_NLP.HybridEngine")


class HybridEngine:
    """
    Hybrid Search Engine for SILLA Recipe Discovery.
    """

    def __init__(
        self,
        db_path: Path = STAGING_DB_PATH,
        dense_weight: float = 0.55,
        sparse_weight: float = 0.45,
        core_boost: float = 0.06,
        title_bonus: float = 0.15,
        rejection_threshold: float = 0.18
    ):
        self.db_path = Path(db_path)
        self.dense_weight = dense_weight
        self.sparse_weight = sparse_weight
        self.core_boost = core_boost
        self.title_bonus = title_bonus
        self.rejection_threshold = rejection_threshold

        logger.info(f"Initializing HybridEngine with database: {self.db_path}")
        self.guard = DomainGuard()
        self.sparse_engine = SparseEngine(db_path=self.db_path)
        self.dense_engine = DenseEngine(db_path=self.db_path)
        self.recipes = self.sparse_engine.recipes
        self.recipe_ids = self.sparse_engine.recipe_ids

        # Precompute title stems and full recipe content stems for all recipes
        self.title_stems_cache = {}
        self.full_content_stems_cache = {}
        for rid, r in self.recipes.items():
            stems_ar = extract_content_stems(r["name_ar"])
            stems_en = extract_content_stems(r["name_en"])
            t_stems = stems_ar | stems_en
            self.title_stems_cache[rid] = t_stems

            ing_text = " ".join(r.get("ingredients_ar", [])) + " " + " ".join(r.get("ingredients_en", []))
            desc_text = (r.get("desc_ar") or "") + " " + (r.get("desc_en") or "")
            self.full_content_stems_cache[rid] = t_stems | extract_content_stems(ing_text) | extract_content_stems(desc_text)

    def search(
        self,
        query: str,
        top_k: int = 3,
        threshold: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Execute full hybrid retrieval pipeline for a user query.
        """
        tau = threshold if threshold is not None else self.rejection_threshold
        bundle = preprocess_query_bundle(query)
        raw_query = bundle["raw_query"]
        norm_query = bundle["normalized_query"]
        q_stems = bundle["content_stems"]
        neg_info = bundle.get("negation_info", {})
        has_neg = neg_info.get("has_negation", False)
        has_alt = neg_info.get("has_alternative", False)
        excluded_stems = neg_info.get("excluded_stems", set())

        # Step 1: Domain & Intent Guard Check
        guard_res = self.guard.inspect(raw_query, norm_query, negation_info=neg_info)
        if not guard_res["is_valid"]:
            decision = guard_res["decision"]
            status = "REQUEST_CLARIFICATION" if decision == "REQUEST_CLARIFICATION" else "REJECTED_GUARD"
            return {
                "query": raw_query,
                "normalized_query": norm_query,
                "is_valid": False,
                "status": status,
                "guard_decision": decision,
                "rejection_reason_ar": guard_res["reason_ar"],
                "rejection_reason_en": guard_res["reason_en"],
                "top_score": 0.0,
                "results": []
            }

        # Step 2: Determine Effective Retrieval Query Text
        search_query = norm_query
        effective_stems = q_stems
        if has_neg and has_alt:
            from SILLA_NLP.preprocessing.query_preprocessor import clean_query_text
            search_query = clean_query_text(neg_info["positive_query"])
            effective_stems = extract_content_stems(search_query)

        # Step 3: Compute Sparse & Dense Similarity Scores
        sparse_scores = dict(self.sparse_engine.search(search_query, top_k=len(self.recipe_ids)))
        dense_scores = self.dense_engine.get_all_scores(search_query)

        # Identify informative food ingredient stems (excluding conversational modifiers)
        generic_tokens = {
            "سهل", "سهله", "سهلة", "سريع", "سريعه", "سريعة", "صحي", "صحيه", "صحية",
            "لذيذ", "لذيذه", "لذيذة", "شهي", "شهيه", "شهية", "طازج", "طازجه", "طازجة",
            "جديد", "جديده", "جديدة", "بسيط", "بسيطه", "بسيطة", "حلو", "حلوه", "حلوة",
            "ممكن", "عايز", "عاوز", "اريد", "أريد", "محتاج", "وصفه", "وصفة", "اكله", "أكلة", "اكلة", "وجبه", "وجبة",
            "عندي", "اقدر", "أقدر", "ايه", "إيه", "بيهم", "فيه", "فيها", "عليا", "مناسب", "مناسبة", "مناسبه",
            "اقترح", "اقترحي", "عمل", "طريقة", "تحضير",
            "ابحث", "أبحث", "بحث", "سيدي", "بص", "شوية", "شويه", "حاجات", "تلاجة", "تلاجه", "التلاجة", "التلاجه", "استفيد", "أستفيد", "ينفع", "غير", "معنديش", "ماعنديش", "تكون", "يكون", "مجهود",
            "تمام", "تماما", "تماماً", "خالص", "نهائي", "نهائيا", "نهائياً", "اصلا", "أصلا", "أصلاً",
            "نباتي", "نباتيه", "نباتية", "حيواني", "حيوانيه", "حيوانية",
            "quick", "fast", "healthy", "fresh", "delicious", "easy", "good", "nice", "tasty", "simple",
            "meal", "dish", "dishes", "meals", "something", "anything", "recipe", "suggest", "want", "need", "can", "you", "give",
            "idea", "ideas", "homemade", "affordable", "budget", "should", "cook", "what", "wanna", "somethin", "vegetarian", "vegan"
        }
        q_food_stems = {s for s in effective_stems if s not in generic_tokens and len(s) > 1}

        # Vegetarian Query Detection (Arabic & English)
        is_veg_query = any(w in raw_query.lower() or w in search_query.lower() for w in ["نباتي", "نباتيه", "نباتية", "vegetarian", "vegan"])
        veg_prohibited_stems = {
            "لحم", "لحمه", "لحوم", "meat", "beef", "بتلو", "ضان", "ضاني", "lamb", "mutton", "veal", "مفروم", "مفرومة",
            "دجاج", "فراخ", "chicken", "اوراك", "صدور", "poultry", "سمك", "fish", "seafood", "جمبري", "shrimp",
            "تونة", "تونه", "سالمون", "salmon", "tuna", "كفتة", "شاورما", "كباب",
            "حبار", "كاليماري", "calamari", "squid", "اخطبوط", "octopus", "كابوريا", "crab", "استاكوزا", "lobster"
        }

        # Step 4: Fusion and Re-ranking
        candidates = []
        for rid in self.recipe_ids:
            r_info = self.recipes[rid]

            # Hard Negative / Exclusion Filter: strictly disqualify recipes with excluded ingredient!
            if has_neg and (excluded_stems & self.full_content_stems_cache[rid]):
                continue

            # Hard Vegetarian Filter: strictly disqualify recipes with any meat, poultry, or seafood!
            if is_veg_query and (veg_prohibited_stems & self.full_content_stems_cache[rid]):
                continue

            s_score = sparse_scores.get(rid, 0.0)
            d_score = dense_scores.get(rid, 0.0)

            # Base Blended Score
            base_score = (self.dense_weight * d_score) + (self.sparse_weight * s_score)

            # Check Title Stem Overlap Bonus
            title_stems = self.title_stems_cache[rid]
            overlap = effective_stems & title_stems
            overlap_bonus = 0.0
            if overlap:
                overlap_ratio = len(overlap) / max(len(effective_stems), 1)
                overlap_bonus = self.title_bonus * overlap_ratio

            # Core Recipe Boost (only for genuinely relevant core candidates)
            core_applied = 0.0
            is_relevant = (overlap_bonus > 0) or (s_score >= 0.05) or (d_score >= 0.48) or (is_veg_query and r_info.get("category") in {"vegan", "vegetarian"})
            if r_info["is_core"] and is_relevant:
                core_applied = self.core_boost

            # Multi-Ingredient Co-occurrence Coordination Bonus / Penalty
            multi_ing_bonus = 0.0
            matched_food = q_food_stems & self.full_content_stems_cache[rid]
            if len(q_food_stems) >= 2:
                cov = len(matched_food) / len(q_food_stems)
                if cov == 1.0:
                    multi_ing_bonus = 0.15
                elif cov >= 0.5:
                    multi_ing_bonus = -0.06
                else:
                    multi_ing_bonus = -0.15

            # Ground / Minced meat penalty for whole meat cuts lacking minced meat
            minced_penalty = 0.0
            if "مفروم" in effective_stems or "مفرومة" in effective_stems:
                if "مفروم" not in self.full_content_stems_cache[rid]:
                    minced_penalty = -0.15

            # Final Hybrid Score
            final_score = base_score + overlap_bonus + core_applied + multi_ing_bonus + minced_penalty

            # Build Match Rationale
            rationales = []
            if s_score > 0.08:
                rationales.append("مطابقة لفظية قوية للكلمات والمكونات")
            if d_score > 0.40:
                rationales.append("تشابه دلالي عالي مع موضوع الوصفة")
            if overlap:
                rationales.append(f"تطابق في عنوان الوصفة: {', '.join(sorted(list(overlap)))}")
            if multi_ing_bonus >= 0.08:
                rationales.append(f"تطابق المكونات المطلوبة معاً: {', '.join(sorted(list(matched_food)))}")
            if has_neg and neg_info.get("excluded_items"):
                rationales.append(f"استبعاد مكون: {', '.join(neg_info['excluded_items'])}")
            if is_veg_query:
                rationales.append("وصفة نباتية معتمدة خالية من اللحوم والدواجن والأسماك")
            if core_applied > 0:
                rationales.append("وصفة رئيسية أصيلة موثقة")

            rationale_str = " | ".join(rationales) if rationales else "تشابه سياقي عام"

            candidates.append({
                "recipe_id": rid,
                "recipe_name_ar": r_info["name_ar"],
                "recipe_name_en": r_info["name_en"],
                "cuisine": r_info["cuisine"],
                "category": r_info["category"],
                "description_ar": r_info["desc_ar"],
                "description_en": r_info["desc_en"],
                "is_core": r_info["is_core"],
                "hybrid_score": round(float(final_score), 4),
                "dense_score": round(float(d_score), 4),
                "sparse_score": round(float(s_score), 4),
                "boost_applied": round(float(core_applied + overlap_bonus + multi_ing_bonus), 4),
                "match_rationale": rationale_str
            })

        # Sort candidates descending by hybrid_score
        candidates.sort(key=lambda x: x["hybrid_score"], reverse=True)
        top_candidates = candidates[:top_k]
        top_score = top_candidates[0]["hybrid_score"] if top_candidates else 0.0

        # Step 4: Quality & Low-Confidence Threshold Verification
        top = top_candidates[0] if top_candidates else None
        if not top:
            return {
                "query": raw_query,
                "normalized_query": norm_query,
                "is_valid": False,
                "status": "REJECTED_LOW_CONFIDENCE",
                "guard_decision": "LOW_CONFIDENCE_MATCH",
                "rejection_reason_ar": "لم يتم العثور على أي نتائج للطلب.",
                "rejection_reason_en": "No recipe candidates found.",
                "top_score": 0.0,
                "results": []
            }

        has_lexical_grounding = (top["sparse_score"] >= 0.03) or (top["boost_applied"] > 0 and "تطابق في عنوان" in top["match_rationale"]) or is_veg_query
        effective_tau = tau if has_lexical_grounding else max(tau, 0.28)

        if top_score < effective_tau:
            return {
                "query": raw_query,
                "normalized_query": norm_query,
                "is_valid": False,
                "status": "REJECTED_LOW_CONFIDENCE",
                "guard_decision": "LOW_CONFIDENCE_MATCH",
                "rejection_reason_ar": f"لم يتم العثور على وصفة مطابقة بدرجة ثقة كافية (أعلى نتيجة: {top_score:.3f}، الحد الأدنى: {effective_tau:.3f}).",
                "rejection_reason_en": f"No high-confidence recipe match found (top score: {top_score:.3f}, threshold: {effective_tau:.3f}).",
                "top_score": top_score,
                "results": []
            }

        return {
            "query": raw_query,
            "normalized_query": norm_query,
            "is_valid": True,
            "status": "SUCCESS",
            "guard_decision": "ACCEPT",
            "rejection_reason_ar": None,
            "rejection_reason_en": None,
            "top_score": top_score,
            "results": top_candidates
        }
