"""
backend/routes/recommendations.py
=================================
Recipe Recommendations Route.
"""

from fastapi import APIRouter, HTTPException
from backend.schemas.schemas import RecommendationRequest
from SILLA_Recommendation.api import get_recommendations
from backend.services.db_service import get_recipe_detail

router = APIRouter()


@router.post("/recommendations")
def recommend_recipes(payload: RecommendationRequest):
    """
    Provides smart recommendations based on craving query, pantry items,
    dietary preferences, or budget constraints.
    """
    try:
        if payload.query:
            result = get_recommendations(
                query=payload.query,
                top_k=payload.top_k,
            )
            return result
        elif payload.recipe_id:
            # Content-based recommendation via Data Science module
            from SILLA_Data_Science.recommender import ContentRecommender
            recommender = ContentRecommender()
            similars = recommender.similar_recipes(payload.recipe_id, top_n=payload.top_k)
            
            # Enrich results
            items = []
            for item in similars:
                rid = item.get("recipe_id")
                detail = get_recipe_detail(rid)
                if detail:
                    item["recipe_name_ar"] = detail["recipe_name_ar"]
                    item["recipe_name_en"] = detail["recipe_name_en"]
                    item["image_url"] = detail["image_url"]
                    item["difficulty"] = detail["difficulty"]
                items.append(item)
            return {"recommendations": items}
        else:
            return {"recommendations": []}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Recommendation failed: {str(e)}")
