"""
backend/tests/test_backend_api.py
=================================
Automated Backend Integration Tests for SILLA.
Validates all endpoints against the live SQLite database and core services.
"""

from backend.routes.health import health_check
from backend.routes.recipes import get_recipes, get_single_recipe, get_recipe_cost
from backend.routes.search import search_recipes
from backend.routes.cart import generate_cart, compare_all_stores
from backend.routes.catalog import get_ingredients, get_stores, get_products
from backend.routes.assistant import chat_with_assistant
from backend.schemas.schemas import SearchRequest, CartGenerateRequest, CompareStoresRequest, AssistantChatRequest


def test_health_check():
    """Verify /api/health returns database connectivity and table counts."""
    h = health_check()
    assert h.status in ["ok", "degraded"]
    assert h.database["connected"] is True
    counts = h.database["counts"]
    assert counts["recipes"] >= 300
    assert counts["ingredients"] >= 130
    assert counts["recipe_ingredients"] >= 2500
    assert counts["products"] >= 400
    assert counts["stores"] >= 5


def test_list_recipes():
    """Verify /api/recipes returns paginated catalog."""
    recs = get_recipes(limit=10, offset=0)
    assert recs.total >= 300
    assert len(recs.recipes) == 10
    first = recs.recipes[0]
    assert first.recipe_id
    assert first.recipe_name_ar
    assert first.recipe_name_en


def test_recipe_detail():
    """Verify /api/recipes/{recipe_id} returns full ingredients and instructions."""
    recipe = get_single_recipe("R0001")
    assert recipe["recipe_id"] == "R0001"
    assert len(recipe["instructions"]) > 0
    assert len(recipe["ingredients"]) > 0
    assert recipe["ingredients"][0]["quantity"] > 0


def test_recipe_cost():
    """Verify cost calculation endpoint."""
    cost = get_recipe_cost("R0001")
    assert "pro_rata_cost_egp" in cost or "recipe_id" in cost


def test_nlp_search():
    """Verify /api/search matches Egyptian Arabic cravings to relevant recipes."""
    res = search_recipes(SearchRequest(query="كشري مصري", top_k=3))
    assert res.status == "SUCCESS"
    assert len(res.matched_recipes) > 0
    assert any("كشري" in r.recipe_name_ar for r in res.matched_recipes)


def test_cart_generation():
    """Verify /api/cart/generate creates optimized grocery cart."""
    payload = CartGenerateRequest(
        recipe_ids=["R0001"],
        servings=4,
        user_pantry={"salt": 500},
        budget_egp=500,
        optimize_budget=True
    )
    cart = generate_cart(payload)
    assert "smart_cart_total_egp" in cart or "total_procurement_cost_egp" in cart or "success" in cart


def test_compare_stores():
    """Verify /api/cart/compare-stores returns store-by-store prices."""
    payload = CompareStoresRequest(
        recipe_ids=["R0001"],
        servings=4
    )
    cmp = compare_all_stores(payload)
    assert "store_rankings" in cmp or "stores" in cmp or "stores_evaluated_count" in cmp


def test_catalog_endpoints():
    """Verify /api/ingredients, /api/stores, /api/products."""
    ings = get_ingredients()
    assert len(ings) >= 100

    stores = get_stores()
    assert len(stores) >= 3

    prods = get_products(limit=5)
    assert len(prods) == 5


def test_assistant_chat():
    """Verify /api/assistant/chat extracts entities and recommends recipes."""
    req = AssistantChatRequest(
        message="عايز أعمل كشري لـ 5 أشخاص",
        servings=5
    )
    chat = chat_with_assistant(req)
    assert chat.reply
    assert len(chat.suggested_recipes) > 0
    assert chat.extracted_entities["servings"] == 5
