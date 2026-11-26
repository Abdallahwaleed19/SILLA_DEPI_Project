"""
backend/routes/cart.py
======================
Smart Shopping Cart Generation and Store Price Comparison Routes.
"""

from fastapi import APIRouter, HTTPException
from backend.schemas.schemas import CartGenerateRequest, CompareStoresRequest
from SILLA_Recommendation.api import build_cart, compare_stores

router = APIRouter()


@router.post("/cart/generate")
def generate_cart(payload: CartGenerateRequest):
    """
    Build an optimized shopping cart:
    - Scales ingredients to user-requested servings
    - Subtracts items already in user's pantry
    - Matches real supermarket products and packages
    - Optimizes package quantities to minimize waste/cost
    - Handles substitutions if items are out of stock
    - Respects user budget constraints
    """
    try:
        cart = build_cart(
            recipe_ids=payload.recipe_ids,
            store_id=payload.store_id,
            servings=payload.servings,
            user_pantry=payload.user_pantry,
            budget_egp=payload.budget_egp,
            enable_substitutes=payload.enable_substitutes,
            optimize_budget=payload.optimize_budget,
        )
        return cart
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Cart generation failed: {str(e)}")


@router.post("/cart/compare-stores")
def compare_all_stores(payload: CompareStoresRequest):
    """
    Compare total cart cost, product coverage, and availability
    across all available Egyptian supermarket stores.
    """
    try:
        return compare_stores(
            recipe_ids=payload.recipe_ids,
            servings=payload.servings,
            user_pantry=payload.user_pantry,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Store comparison failed: {str(e)}")
