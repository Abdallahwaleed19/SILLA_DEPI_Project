"""
backend/routes/search.py
========================
Semantic & Hybrid NLP Search Route.
"""

from fastapi import APIRouter
from backend.schemas.schemas import SearchRequest, SearchResponse
from SILLA_NLP.api import match_recipe
from backend.services.db_service import get_recipe_detail

router = APIRouter()


@router.post("/search", response_model=SearchResponse)
def search_recipes(payload: SearchRequest):
    """
    Process natural-language food cravings (Egyptian Arabic, Standard Arabic, or English)
    using SILLA's hybrid dense-sparse NLP retrieval engine.
    """
    result = match_recipe(
        query=payload.query,
        language=payload.language,
        top_k=payload.top_k,
        threshold=payload.threshold
    )

    # Enrich matched recipes with image_url if available in database
    matched_recipes = result.get("matched_recipes", [])
    for rec in matched_recipes:
        rid = rec.get("recipe_id")
        if rid:
            detail = get_recipe_detail(rid)
            if detail and detail.get("image_url"):
                rec["image_url"] = detail["image_url"]

    return SearchResponse(
        status=result.get("status", "SUCCESS"),
        query=result.get("query", payload.query),
        normalized_query=result.get("normalized_query"),
        language=result.get("language"),
        matched_recipes=matched_recipes,
        rejection_reason=result.get("rejection_reason"),
        rejection_reason_en=result.get("rejection_reason_en"),
        clarification_message=result.get("clarification_message"),
        execution_time_ms=result.get("execution_time_ms", 0.0)
    )
