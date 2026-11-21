"""
SILLA_Recommendation/recommendation_engine.py
=============================================
Recommendation Engine for SILLA:
- Consumes SILLA_NLP.match_recipe output directly without altering NLP weights.
- Evaluates ingredient product availability and cooking feasibility.
- Calculates empirical recipe costs (net consumed & whole package procurement).
- Strictly suppresses rejected or contradictory queries (returns 0 recipes).
- Ranks candidate recipes based on semantic match + product availability + core authenticity.
"""

from pathlib import Path
from typing import Dict, List, Optional, Any

try:
    from SILLA_NLP import match_recipe
except (ImportError, ModuleNotFoundError):
    match_recipe = None
from SILLA_Recommendation.config import (
    DB_PATH,
    NLP_SCORE_WEIGHT,
    AVAILABILITY_WEIGHT,
    CORE_RECIPE_BOOST,
    CORE_EGYPTIAN_RECIPE_IDS,
    MIN_COVERAGE_THRESHOLD,
)
from SILLA_Recommendation.cost_calculator import CostCalculator


class RecommendationEngine:
    """
    Ranks and enriches recipe recommendations by fusing NLP intent signals,
    ingredient inventory availability, and pricing realities.
    """

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = Path(db_path)
        self.cost_calculator = CostCalculator(self.db_path)

    def _get_connection(self):
        import sqlite3
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def recommend(
        self,
        query: str,
        language: Optional[str] = None,
        top_k: int = 3,
        store_id: Optional[str] = None,
        min_coverage: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Generate ranked recipe recommendations with cost calculation.
        
        Args:
            query: User search text (Arabic, Egyptian slang, or English).
            language: Optional language hint ('ar' or 'en').
            top_k: Number of ranked recommendations to return.
            store_id: Optional supermarket ID filter (e.g. 'STR001').
            min_coverage: Optional filter for minimum ingredient price coverage.
            
        Returns:
            Dictionary containing query status, intent message, and ranked recommendations.
        """
        # 1. Query NLP Engine (with lightweight SQL keyword fallback if numpy/NLP dependencies are absent)
        if match_recipe is not None:
            nlp_result = match_recipe(query, language=language, top_k=max(top_k * 2, 6))
        else:
            with self._get_connection() as conn:
                q_clean = query.strip()
                rows = conn.execute(
                    "SELECT recipe_id, recipe_name_ar, recipe_name_en FROM recipes WHERE recipe_name_ar LIKE ? OR recipe_name_en LIKE ? LIMIT ?",
                    (f"%{q_clean}%", f"%{q_clean}%", max(top_k * 2, 6))
                ).fetchall()
                matched = [
                    {
                        "recipe_id": r["recipe_id"],
                        "recipe_name_ar": r["recipe_name_ar"],
                        "recipe_name_en": r["recipe_name_en"],
                        "similarity_score": 0.85,
                    }
                    for r in rows
                ]
                nlp_result = {
                    "status": "SUCCESS" if matched else "NO_MATCH",
                    "matched_recipes": matched,
                    "rejection_reason": None if matched else "No recipe matched search keywords",
                    "clarification_message": None,
                }

        status = nlp_result.get("status")
        rejection_msg = (
            nlp_result.get("rejection_reason")
            or nlp_result.get("clarification_message")
            or nlp_result.get("message")
        )

        # 2. Domain, Intent & Contradiction Guard Suppression
        # If NLP rejected or asked for clarification, do NOT display any recipes
        if status != "SUCCESS":
            return {
                "status": status,
                "message": rejection_msg,
                "query": query,
                "total_recommendations": 0,
                "recommendations": [],
                "guard_triggered": True,
            }

        # NLP matches field in SILLA_NLP is 'matched_recipes'
        nlp_matches = nlp_result.get("matched_recipes") or []
        if not nlp_matches:
            return {
                "status": "NO_MATCHES_FOUND",
                "message": "لم يتم العثور على وصفات مطابقة لطلبك.",
                "query": query,
                "total_recommendations": 0,
                "recommendations": [],
                "guard_triggered": False,
            }

        # 3. Enrich Candidates with Cost & Availability
        candidates = []
        for match in nlp_matches:
            recipe_id = match["recipe_id"]
            nlp_score = float(match.get("similarity_score", 0.0))

            # Calculate cost and ingredient coverage
            cost_info = self.cost_calculator.calculate_recipe_cost(recipe_id, store_id=store_id)
            if not cost_info.get("success", False):
                continue

            coverage = float(cost_info.get("price_completeness_ratio", 0.0))

            # Apply minimum coverage threshold if specified
            if coverage < min_coverage:
                continue

            # Core Egyptian recipe authenticity boost
            core_boost = CORE_RECIPE_BOOST if recipe_id in CORE_EGYPTIAN_RECIPE_IDS else 0.0

            # Composite Recommendation Score:
            # Multiplicatively modulates NLP score by ingredient availability
            # S_rec = S_nlp * (0.70 + 0.30 * Coverage) + CoreBoost
            rec_score = (nlp_score * (0.70 + 0.30 * coverage)) + core_boost

            # Feasibility Tier
            if coverage >= 1.0:
                feasibility_tier = "FULL_FEASIBILITY"
            elif coverage >= 0.70:
                feasibility_tier = "HIGH_FEASIBILITY"
            elif coverage >= 0.40:
                feasibility_tier = "MODERATE_FEASIBILITY"
            else:
                feasibility_tier = "LOW_FEASIBILITY"

            candidates.append({
                "recipe_id": recipe_id,
                "recipe_name_ar": cost_info["recipe_name_ar"],
                "recipe_name_en": cost_info["recipe_name_en"],
                "cuisine": cost_info["cuisine"],
                "category": cost_info["category"],
                "base_servings": cost_info["base_servings"],
                # Scoring
                "recommendation_score": round(rec_score, 4),
                "nlp_similarity_score": round(nlp_score, 4),
                "ingredient_coverage_ratio": round(coverage, 4),
                "feasibility_tier": feasibility_tier,
                # Cost Details
                "net_recipe_cost_egp": cost_info["net_recipe_cost_egp"],
                "net_cost_per_serving_egp": cost_info["net_cost_per_serving_egp"],
                "grocery_procurement_cost_egp": cost_info["grocery_procurement_cost_egp"],
                "procurement_cost_per_serving_egp": cost_info["procurement_cost_per_serving_egp"],
                # Ingredient Counts
                "total_ingredients_count": cost_info["total_ingredients_count"],
                "priced_ingredients_count": cost_info["priced_ingredients_count"],
                "unpriced_ingredients_count": cost_info["unpriced_ingredients_count"],
                "is_fully_priced": cost_info["is_fully_priced"],
                "pricing_disclaimer": cost_info["pricing_disclaimer"],
                "unpriced_ingredients": cost_info["unpriced_ingredients"],
                "store_id": store_id,
            })

        # 4. Rank Candidates Descending by Recommendation Score
        candidates.sort(
            key=lambda x: (x["recommendation_score"], x["ingredient_coverage_ratio"]),
            reverse=True
        )

        ranked = candidates[:top_k]

        return {
            "status": "SUCCESS",
            "message": None,
            "query": query,
            "store_id": store_id,
            "total_recommendations": len(ranked),
            "recommendations": ranked,
            "guard_triggered": False,
        }
