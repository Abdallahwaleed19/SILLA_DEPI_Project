"""
SILLA_Recommendation/api.py
===========================
Clean, high-level public interface for SILLA Recommendation & Cost Engine.
"""

from typing import Dict, List, Optional, Any, Union
from pathlib import Path

from SILLA_Recommendation.config import DB_PATH
from SILLA_Recommendation.recommendation_engine import RecommendationEngine
from SILLA_Recommendation.cost_calculator import CostCalculator
from SILLA_Recommendation.smart_cart import SmartCart
from SILLA_Recommendation.cart_builder import CartBuilder

# Cached singleton instances for fast repeated API calls
_rec_engine: Optional[RecommendationEngine] = None
_cost_calculator: Optional[CostCalculator] = None
_smart_cart: Optional[SmartCart] = None
_cart_builder: Optional[CartBuilder] = None


def get_recommendation_engine(db_path: Path = DB_PATH) -> RecommendationEngine:
    global _rec_engine
    if _rec_engine is None or _rec_engine.db_path != db_path:
        _rec_engine = RecommendationEngine(db_path=db_path)
    return _rec_engine


def get_cost_calculator(db_path: Path = DB_PATH) -> CostCalculator:
    global _cost_calculator
    if _cost_calculator is None or _cost_calculator.db_path != db_path:
        _cost_calculator = CostCalculator(db_path=db_path)
    return _cost_calculator


def get_smart_cart(db_path: Path = DB_PATH) -> SmartCart:
    global _smart_cart
    if _smart_cart is None or _smart_cart.db_path != db_path:
        _smart_cart = SmartCart(db_path=db_path)
    return _smart_cart


def get_cart_builder(db_path: Path = DB_PATH) -> CartBuilder:
    global _cart_builder
    if _cart_builder is None or _cart_builder.db_path != db_path:
        _cart_builder = CartBuilder(db_path=db_path)
    return _cart_builder


def get_recommendations(
    query: str,
    language: Optional[str] = None,
    top_k: int = 3,
    store_id: Optional[str] = None,
    min_coverage: float = 0.0,
    db_path: Path = DB_PATH
) -> Dict[str, Any]:
    """
    Get ranked recipe recommendations with cost calculation and feasibility analysis.
    """
    engine = get_recommendation_engine(db_path=db_path)
    return engine.recommend(
        query=query,
        language=language,
        top_k=top_k,
        store_id=store_id,
        min_coverage=min_coverage,
    )


def calculate_recipe_cost(
    recipe_id: str,
    store_id: Optional[str] = None,
    db_path: Path = DB_PATH
) -> Dict[str, Any]:
    """
    Calculate pro-rata net recipe cost and whole package grocery procurement cost.
    """
    calc = get_cost_calculator(db_path=db_path)
    return calc.calculate_recipe_cost(recipe_id=recipe_id, store_id=store_id)


def build_smart_cart(
    recipe_ids: List[str],
    store_id: Optional[str] = None,
    servings: Optional[Union[int, float, Dict[str, float]]] = None,
    user_pantry: Optional[Any] = None,
    budget_egp: Optional[float] = None,
    enable_substitutes: bool = True,
    optimize_budget: bool = True,
    db_path: Path = DB_PATH
) -> Dict[str, Any]:
    """
    Build an optimized multi-recipe shopping cart that consolidates common ingredients.
    """
    builder = get_cart_builder(db_path=db_path)
    return builder.build_cart(
        recipe_ids=recipe_ids,
        servings=servings,
        user_pantry=user_pantry,
        store_id=store_id,
        budget_egp=budget_egp,
        enable_substitutes=enable_substitutes,
        optimize_budget=optimize_budget,
    )


def build_cart(
    recipe_ids: List[str],
    servings: Optional[Union[int, float, Dict[str, float]]] = None,
    user_pantry: Optional[Any] = None,
    store_id: Optional[str] = None,
    budget_egp: Optional[float] = None,
    enable_substitutes: bool = True,
    optimize_budget: bool = True,
    db_path: Path = DB_PATH
) -> Dict[str, Any]:
    """
    Convenience alias for CartBuilder.build_cart.
    """
    return build_smart_cart(
        recipe_ids=recipe_ids,
        store_id=store_id,
        servings=servings,
        user_pantry=user_pantry,
        budget_egp=budget_egp,
        enable_substitutes=enable_substitutes,
        optimize_budget=optimize_budget,
        db_path=db_path,
    )


def compare_stores(
    recipe_ids: List[str],
    servings: Optional[Union[int, float, Dict[str, float]]] = None,
    user_pantry: Optional[Any] = None,
    db_path: Path = DB_PATH
) -> Dict[str, Any]:
    """
    Compare grocery cart pricing and availability across all registered stores.
    """
    builder = get_cart_builder(db_path=db_path)
    return builder.compare_stores(
        recipe_ids=recipe_ids,
        servings=servings,
        user_pantry=user_pantry,
    )
