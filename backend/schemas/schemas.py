"""
backend/schemas/schemas.py
==========================
Pydantic Request & Response Schemas for SILLA Backend API.
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field


# --- Health ---
class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"
    environment: str
    database: Dict[str, Any]
    modules: Dict[str, bool]


# --- Recipe Schemas ---
class IngredientItem(BaseModel):
    ingredient_id: Optional[str] = None
    original_name: str
    canonical_name_ar: Optional[str] = None
    canonical_name_en: Optional[str] = None
    quantity: float
    unit: str
    is_optional: bool = False
    preparation_note: Optional[str] = None


class RecipeSummary(BaseModel):
    recipe_id: str
    recipe_name_en: str
    recipe_name_ar: str
    description: Optional[str] = None
    description_ar: Optional[str] = None
    cuisine: Optional[str] = None
    category: Optional[str] = None
    base_servings: float = 4.0
    prep_time_min: int = 15
    cook_time_min: int = 25
    difficulty: Optional[str] = "Medium"
    image_url: Optional[str] = None
    estimated_cost_egp: Optional[float] = None


class RecipeDetail(RecipeSummary):
    instructions: List[str] = []
    ingredients: List[IngredientItem] = []


class RecipeListResponse(BaseModel):
    total: int
    offset: int
    limit: int
    recipes: List[RecipeSummary]


# --- NLP Search Schemas ---
class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Natural language food craving in Arabic or English")
    language: Optional[str] = None
    top_k: int = Field(default=5, ge=1, le=20)
    threshold: Optional[float] = None


class MatchedRecipe(BaseModel):
    recipe_id: str
    recipe_name_ar: str
    recipe_name_en: str
    cuisine: Optional[str] = None
    category: Optional[str] = None
    similarity_score: float
    match_reason: Optional[str] = None
    is_core_recipe: bool = False
    description_ar: Optional[str] = None
    description_en: Optional[str] = None
    image_url: Optional[str] = None
    estimated_cost_egp: Optional[float] = None


class SearchResponse(BaseModel):
    status: str
    query: str
    normalized_query: Optional[str] = None
    language: Optional[str] = None
    matched_recipes: List[MatchedRecipe] = []
    rejection_reason: Optional[str] = None
    rejection_reason_en: Optional[str] = None
    clarification_message: Optional[str] = None
    execution_time_ms: float = 0.0


# --- Smart Cart Schemas ---
class CartGenerateRequest(BaseModel):
    recipe_ids: List[str] = Field(..., min_items=1, description="List of recipe IDs to cook")
    servings: Optional[Union[int, float, Dict[str, float]]] = None
    user_pantry: Optional[Any] = None
    store_id: Optional[str] = None
    budget_egp: Optional[float] = None
    enable_substitutes: bool = True
    optimize_budget: bool = True


class CompareStoresRequest(BaseModel):
    recipe_ids: List[str] = Field(..., min_items=1)
    servings: Optional[Union[int, float, Dict[str, float]]] = None
    user_pantry: Optional[Any] = None


# --- Recommendation Schemas ---
class RecommendationRequest(BaseModel):
    query: Optional[str] = None
    recipe_id: Optional[str] = None
    diet: Optional[str] = None
    pantry: Optional[List[str]] = None
    budget_egp: Optional[float] = None
    max_time_min: Optional[int] = None
    top_k: int = 5


# --- Assistant / Chat Schemas ---
class AssistantChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    session_id: Optional[str] = None
    active_recipes: Optional[List[str]] = None
    pantry: Optional[List[str]] = None
    budget_egp: Optional[float] = None
    servings: Optional[int] = None


class AssistantChatResponse(BaseModel):
    reply: str
    suggested_recipes: List[RecipeSummary] = []
    extracted_entities: Dict[str, Any] = {}
    actions: List[Dict[str, Any]] = []
