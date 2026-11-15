"""
SILLA_Recommendation
====================
Recommendation Engine, Empirical Cost Calculation & Smart Multi-Recipe Cart
for SILLA — Smart Recipe Discovery and Shopping Assistant.
"""

from SILLA_Recommendation.config import (
    DB_PATH,
    STAGING_DB_PATH,
    PRODUCTION_DB_PATH,
    NLP_SCORE_WEIGHT,
    AVAILABILITY_WEIGHT,
    CORE_RECIPE_BOOST,
    MIN_COVERAGE_THRESHOLD,
    STANDARD_UNIT_CONVERSIONS,
    PRODUCE_PIECE_WEIGHT_G,
)
from SILLA_Recommendation.cost_calculator import (
    UnitConverter,
    CostCalculator,
)
from SILLA_Recommendation.recommendation_engine import (
    RecommendationEngine,
)
from SILLA_Recommendation.smart_cart import (
    SmartCart,
)
from SILLA_Recommendation.api import (
    get_recommendations,
    calculate_recipe_cost,
    build_smart_cart,
    get_recommendation_engine,
    get_cost_calculator,
    get_smart_cart,
)

__all__ = [
    "DB_PATH",
    "STAGING_DB_PATH",
    "PRODUCTION_DB_PATH",
    "NLP_SCORE_WEIGHT",
    "AVAILABILITY_WEIGHT",
    "CORE_RECIPE_BOOST",
    "MIN_COVERAGE_THRESHOLD",
    "STANDARD_UNIT_CONVERSIONS",
    "PRODUCE_PIECE_WEIGHT_G",
    "UnitConverter",
    "CostCalculator",
    "RecommendationEngine",
    "SmartCart",
    "get_recommendations",
    "calculate_recipe_cost",
    "build_smart_cart",
    "get_recommendation_engine",
    "get_cost_calculator",
    "get_smart_cart",
]
