"""
backend/routes/recipes.py
=========================
Recipe Catalog and Detail Routes.
"""

from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from backend.schemas.schemas import RecipeListResponse, RecipeDetail, RecipeSummary
from backend.services.db_service import list_recipes, get_recipe_detail
from SILLA_Recommendation.api import calculate_recipe_cost

router = APIRouter()


@router.get("/recipes", response_model=RecipeListResponse)
def get_recipes(
    search: Optional[str] = Query(None, description="Search by title or description"),
    category: Optional[str] = Query(None, description="Filter by category"),
    cuisine: Optional[str] = Query(None, description="Filter by cuisine"),
    limit: int = Query(400, ge=1, le=1000),
    offset: int = Query(0, ge=0)
):
    """
    Retrieve paginated list of recipes with optional filters.
    """
    total, recipes = list_recipes(
        search=search,
        category=category,
        cuisine=cuisine,
        limit=limit,
        offset=offset
    )
    return RecipeListResponse(
        total=total,
        offset=offset,
        limit=limit,
        recipes=recipes
    )


@router.get("/recipes/{recipe_id}", response_model=RecipeDetail)
def get_single_recipe(recipe_id: str):
    """
    Retrieve full details for a single recipe, including ingredients and instructions.
    """
    recipe = get_recipe_detail(recipe_id)
    if not recipe:
        raise HTTPException(status_code=404, detail=f"Recipe '{recipe_id}' not found.")
    
    # Calculate estimated cost if possible
    try:
        cost_info = calculate_recipe_cost(recipe_id=recipe_id)
        recipe["estimated_cost_egp"] = cost_info.get("pro_rata_cost_egp")
    except Exception:
        pass

    return recipe


@router.get("/recipes/{recipe_id}/cost")
def get_recipe_cost(recipe_id: str, store_id: Optional[str] = None):
    """
    Calculates detailed procurement and pro-rata cost for a recipe.
    """
    try:
        return calculate_recipe_cost(recipe_id=recipe_id, store_id=store_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
