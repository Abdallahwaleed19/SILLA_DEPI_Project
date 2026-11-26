"""
backend/routes/assistant.py
===========================
SILLA Intelligent Cooking & Shopping Assistant Route.
Processes conversational requests, extracts entities (servings, budget, dish),
matches recipes via NLP engine, and provides smart kitchen guidance.
"""

import re
from typing import Dict, Any, List
from fastapi import APIRouter
from backend.schemas.schemas import AssistantChatRequest, AssistantChatResponse, RecipeSummary
from SILLA_NLP.api import match_recipe
from backend.services.db_service import get_recipe_detail

router = APIRouter()


def extract_servings(text: str) -> int:
    """Extracts number of people/servings from Arabic or English text."""
    # Match patterns like: "4 أفراد", "لـ 5 اشخاص", "for 4 people", "servings: 6"
    ar_match = re.search(r'(?:لـ?|تكفي\s*|حوالي\s*)?(\d+)\s*(?:أفراد|افراد|أشخاص|اشخاص|شخص|وجبات|حصص)', text)
    if ar_match:
        try:
            return int(ar_match.group(1))
        except ValueError:
            pass
    en_match = re.search(r'(?:for\s*)?(\d+)\s*(?:people|persons|servings|portions)', text, re.IGNORECASE)
    if en_match:
        try:
            return int(en_match.group(1))
        except ValueError:
            pass
    return 4


def extract_budget(text: str) -> float:
    """Extracts budget amount in EGP from text if specified."""
    # Match patterns like "300 جنيه", "ميزانية 250 ج", "budget 400 egp"
    ar_match = re.search(r'(?:ميزانية\s*(?:حوالي\s*)?|بـ\s*|بحدود\s*)?(\d+)\s*(?:جنيه|جنيها|ج\.م|جم|ج)', text)
    if ar_match:
        try:
            val = float(ar_match.group(1))
            if val > 15:  # filter out small numbers that might be servings or times
                return val
        except ValueError:
            pass
    en_match = re.search(r'(?:budget\s*(?:of\s*)?)?(\d+)\s*(?:egp|le|pounds)', text, re.IGNORECASE)
    if en_match:
        try:
            return float(en_match.group(1))
        except ValueError:
            pass
    return 0.0


@router.post("/assistant/chat", response_model=AssistantChatResponse)
def chat_with_assistant(payload: AssistantChatRequest):
    """
    Conversational assistant for SILLA.
    """
    query = payload.message.strip()
    servings = payload.servings or extract_servings(query)
    budget = payload.budget_egp or extract_budget(query)
    
    extracted = {
        "servings": servings,
        "budget_egp": budget if budget > 0 else None,
    }

    # Match recipes using SILLA NLP
    nlp_res = match_recipe(query, top_k=3)
    status = nlp_res.get("status")
    matched = nlp_res.get("matched_recipes", [])

    suggested: List[RecipeSummary] = []
    actions: List[Dict[str, Any]] = []

    if status == "SUCCESS" and matched:
        top_recipe = matched[0]
        # Enrich top recipes
        for m in matched:
            detail = get_recipe_detail(m["recipe_id"])
            if detail:
                suggested.append(RecipeSummary(
                    recipe_id=detail["recipe_id"],
                    recipe_name_en=detail["recipe_name_en"],
                    recipe_name_ar=detail["recipe_name_ar"],
                    description=detail.get("description"),
                    description_ar=detail.get("description_ar"),
                    cuisine=detail.get("cuisine"),
                    category=detail.get("category"),
                    base_servings=detail.get("base_servings", 4.0),
                    prep_time_min=detail.get("prep_time_min", 15),
                    cook_time_min=detail.get("cook_time_min", 25),
                    difficulty=detail.get("difficulty", "Medium"),
                    image_url=detail.get("image_url"),
                ))

        reply = (
            f"يا هلا بيك في سيلا! 👩‍🍳 لقد اخترت لك وصفة شهية ومناسبة لطلبك: "
            f"**{top_recipe['recipe_name_ar']}** ({top_recipe['recipe_name_en']}).\n\n"
            f"🍽️ الكمية المحسوبة: **{servings} أفراد**.\n"
        )
        if budget > 0:
            reply += f"💰 الميزانية المحددة: **{budget:.0f} جنيه**.\n"

        reply += (
            f"\nيمكنك الآن استعراض مقادير الوصفة، فحص النواقص بناءً على مخزونك (Pantry)، "
            f"أو التوجه فوراً إلى سلة المشتريات لحساب التكلفة ومقارنتها بين المتاجر!"
        )

        actions.append({
            "type": "VIEW_RECIPE",
            "recipe_id": top_recipe["recipe_id"],
            "title": f"عرض مقادير {top_recipe['recipe_name_ar']}"
        })
        actions.append({
            "type": "BUILD_CART",
            "recipe_ids": [top_recipe["recipe_id"]],
            "servings": servings,
            "title": "حساب السلة ومقارنة الأسعار"
        })

    elif status == "REJECTED_OUT_OF_DOMAIN":
        reply = (
            "أهلاً بك! أنا مساعد سيلا الذكي المخصص للطبخ، والوصفات، وإدارة سلة المشتريات والميزانية في السوبرماركت. 🛒🍲\n"
            "يسعدني مساعدتك في أي أكلة بتشتهيها أو وصفة تبحث عنها بالمقادير والأسعار في مصر!"
        )
    elif status == "REQUEST_CLARIFICATION":
        clarification = nlp_res.get("clarification_message") or "هل يمكنك توضيح اسم الأكلة أو المكونات التي ترغب في طبخها بالتحديد؟"
        reply = f"تسلم! {clarification} 🍳"
    else:
        reply = (
            "عذراً، لم أجد وصفة مطابقة تماماً لطلبك في الداتابيز حالياً. "
            "جرب البحث عن أطباق شهيرة مثل: كشري، مكرونة بشاميل، ملوخية بالفراخ، طاجن بامية، أو شيش طاووق! 🍲"
        )

    return AssistantChatResponse(
        reply=reply,
        suggested_recipes=suggested,
        extracted_entities=extracted,
        actions=actions
    )
