"""
SILLA_NLP/intent_guard/domain_guard.py
======================================
Domain & Intent Guard: Validates whether a user query falls within SILLA's culinary scope.

Features:
- Fast rule-based rejection of non-food products (electronics, apparel, cosmetics, tech).
- High-precision detection of food categories currently outside SILLA's catalog (desserts, sushi, burgers, fast food).
- Detection of fundamentally contradictory / conflicting ingredient requests (e.g. koshari + fish, savory bechamel + jam/sweets).
- Detection of overly ambiguous queries to trigger clarification rather than wild guessing.
- Prevention of single-modifier false positive matches (e.g. matching on 'سريع' alone).
"""

import re
from typing import Dict, Any, Optional

from SILLA_NLP.preprocessing.query_preprocessor import normalize_arabic, stem_arabic_token

# Non-Food Keywords (Immediate Rejection)
NON_FOOD_PATTERNS = [
    r"\bشاحن\b", r"\bموبايل\b", r"\bهاتف\b", r"\bتايب\s*سي\b", r"\bكابل\b", r"\bسلك\b",
    r"\bسماع[ةه]\b", r"\bسماعات\b", r"\bلابتوب\b", r"\bكمبيوتر\b", r"\bشاش[ةه]\b", r"\bتلفزيون\b",
    r"\bقميص\b", r"\bبنطلون\b", r"\bحذاء\b", r"\bملابس\b", r"\bمكياج\b", r"\bعطر\b",
    r"\bبطاري[ةه]\b", r"\bجراب\b", r"\bباور\s*بانك\b", r"\bcharger\b", r"\bcable\b",
    r"\bphone\b", r"\blaptop\b", r"\btype-c\b", r"\bheadphones\b", r"\bbattery\b",
    # Tech, Software, AI, and Programming
    r"\b([وبك]?ل?)(?:ال)?برمج[ةه]\b", r"\b([وبك]?ل?)(?:ال)?مبرمج\b", r"\b([وبك]?ل?)(?:ال)?كود\b", r"\b([وبك]?ل?)(?:ال)?اكواد\b", r"\b([وبك]?ل?)(?:ال)?سوفت\s*وير\b",
    r"\b([وبك]?ل?)(?:ال)?ذكاء\s*(?:ال)?(?:اصطناعي|صناعي)\b", r"\b([وبك]?ل?)(?:ال)?خوارزمي[ةه]\b", r"\b([وبك]?ل?)(?:ال)?داتا\s*ساينس\b",
    r"\bprogramming\b", r"\bsoftware\b", r"\bdeveloper\b", r"\bcoding\b",
    r"\b(?:ai|artificial\s+intelligence|machine\s+learning|deep\s+learning|data\s+science)\b",
    # Vehicles & Transportation
    r"\b([وبك]?ل?)(?:ال)?(سيار[ةه]|عربيت?[ةه]|عربيتي)\b", r"\b([وبك]?ل?)(?:ال)?موتوسيكل\b", r"\b([وبك]?ل?)(?:ال)?طيار[ةه]\b", r"\b([وبك]?ل?)(?:ال)?فندق\b", r"\b([وبك]?ل?)(?:ال)?حجز\b",
    r"\b([وبك]?ل?)(?:ال)?وظائ?ف\b", r"\b([وبك]?ل?)(?:ال)?وظيفة\b", r"\b([وبك]?ل?)(?:ال)?شغل\b",
    # Academic / Science non-food
    r"\b([وبك]?ل?)(?:ال)?رياضيات\b", r"\b([وبك]?ل?)(?:ال)?فيزياء\b", r"\b([وبك]?ل?)(?:ال)?كيمياء\b", r"\b([وبك]?ل?)(?:ال)?تاريخ\b", r"\b([وبك]?ل?)(?:ال)?جغرافيا\b"
]

# Out-of-Catalog Food Categories (Food items not present in the current recipe catalog)
OUT_OF_CATALOG_FOOD_PATTERNS = [
    # Sweets & Desserts
    r"\b([وبك]?ل?)(?:ال)?(مسكر[ةه]?|حاج[ةه]\s+مسكر[ةه]?)\b",
    r"\bتشيز\s*كيك\b", r"\bكيك[ةه]?\b", r"\bتورت[ةه]\b", r"\bشوكولات[ةه]\b",
    r"\bحلويات\b", r"\bحلو[ىي]\b", r"\bبسبوس[ةه]\b", r"\bكناف[ةه]\b", r"\bقطايف\b", r"\bايس\s*كريم\b",
    r"\bدونات\b", r"\bدوناتس\b", r"\bوافل\b", r"\bبان\s*كيك\b", r"\bمهلبي[ةه]\b", r"\bام\s*علي\b",
    r"\bdessert\b", r"\bcheesecake\b", r"\bcake\b", r"\bchocolate\b", r"\bice\s*cream\b",
    # Fast Food Burgers & Chains
    r"\bبرجر\b", r"\bبورجر\b", r"\bبيج\s*ماك\b", r"\bماكدونالدز\b", r"\bكنتاكي\b", r"\bزنجر\b",
    r"\bburger\b", r"\bcheeseburger\b", r"\bbig\s*mac\b", r"\bmcdonalds\b",
    # Japanese / Asian Specialty
    r"\bسوشي\b", r"\bساشيمي\b", r"\bماكي\b", r"\bرامن\b", r"\bنودلز\b", r"\bsushi\b", r"\bsashimi\b", r"\bramen\b",
    # Specialty Fast Food
    r"\bشاورما\b", r"\bكريب\b", r"\bتاكو\b", r"\bshawarma\b", r"\bcrepe\b", r"\btaco\b",
    # Luxury / Gourmet Ingredients & Items
    r"\b([وبك]?ل?)(?:ال)?كافيار\b", r"\b([وبك]?ل?)(?:ال)?زعفران\b", r"\b([وبك]?ل?)(?:ال)?استاكوزا\b", r"\b([وبك]?ل?)(?:ال)?استكوزا\b", r"\b([وبك]?ل?)(?:ال)?كابوريا\b",
    r"\b([وبك]?ل?)(?:ال)?كمأ[ةه]\b", r"\b([وبك]?ل?)(?:ال)?ترافل\b", r"\b([وبك]?ل?)(?:ال)?بطارخ\b", r"\b([وبك]?ل?)(?:ال)?ريزوتو\b",
    r"\bcaviar\b", r"\bsaffron\b", r"\btruffle\b", r"\blobster\b", r"\bcrab\b",
    r"\brisotto\b"
]

# Contradictory / Mutually Incompatible Culinary Combinations
CONFLICT_PATTERNS = [
    # 1. Traditional Koshari with Seafood / Fish
    (
        r"\b([وبك]?ل?)(?:ال)?كشري\b",
        r"\b([وبك]?ل?)(?:ال)?(سمك|تون[ةه]|جمبري|سالمون|سي\s*فود)\b",
        "الطلب يحتوي على تعارض جوهري: الكشري المصري الأصيل لا يُعد بالأسماك أو المأكولات البحرية.",
        "Fundamentally conflicting request: Traditional Egyptian Koshari cannot be made with seafood."
    ),
    # 2. Savory Main Dishes with Sweet / Jam / Dessert Ingredients
    (
        r"\b([وبك]?ل?)(?:ال)?(مكرون[ةه]\s+بشاميل|بشاميل|حواوشي|كفت[ةه]|فت[ةه]|ملوخي[ةه])\b",
        r"\b([وبك]?ل?)(?:ال)?(مرب[ىي]|شوكولات[ةه]|نوتيلا|ايس\s*كريم|حلوى|حلويات|سكر|كاسترد)\b",
        "الطلب يحتوي على تعارض جوهري: لا يمكن دمج أطباق حادقة رئيسية (مثل البشاميل/الكفتة/الحواوشي) مع السكريات والمربى والحلويات.",
        "Fundamentally conflicting request: Savory baked dishes cannot be combined with jams, chocolates, or sweets."
    )
]

# Ambiguous Tokens & Generic Modifiers
AMBIGUOUS_TOKENS = {
    "اكل", "اكله", "أكلة", "اكلة", "اكلات", "أكلات",
    "طعام", "اطعمة", "أطعمة",
    "وجبه", "وجبة", "وجبات",
    "طبخه", "طبخة", "طبخات",
    "حاجه", "حاجة", "اي", "شيء", "شئ",
    "خفيف", "خفيفه", "خفيفة", "وخفيف", "وخفيفه", "وخفيفة",
    "عشا", "عشاء", "وللعشا", "وللعشاء", "للعشا", "للعشاء", "غدا", "غداء", "فطار",
    "بتاع", "بتاعه", "بتاعة", "البيت", "بيت",
    "اعمللي", "اعملي", "اعمل", "سويلي", "طبخلي", "اطبخ", "أطبخ", "رشحلي", "اقترحلي", "هاتلي",
    "عايز", "عاوز", "اريد", "بدي", "محتاج",
    "جعان", "جعانه", "جعانة", "جوعان", "جوعانه", "جوعانة", "انا", "أنا",
    "كده", "كدا", "معايا", "معي", "تعتمد", "يعتمد",
    "مكونات", "ومكونات", "بمكونات", "مكون", "بمكون", "فكرة", "فكره", "وفكرة", "وفكره",
    "food", "foods", "meal", "meals", "dish", "dishes", "something", "anything",
    "suggest", "need", "give", "traditional", "dinner", "lunch", "breakfast", "hungry",
    "idea", "ideas", "homemade", "cook", "should", "what", "wanna", "somethin", "recipe", "recipes",
    "مناسب", "مناسبه", "مناسبة", "ومناسب", "ومناسبه", "ومناسبة"
}

GENERIC_MODIFIERS = {
    "سريع", "سريعه", "سريعة", "وسريع", "وسريعه", "وسريعة",
    "صحي", "صحيه", "صحية", "وصحي", "وصحيه", "وصحية",
    "لذيذ", "لذيذه", "لذيذة", "ولذيذ", "ولذيذه", "ولذيذة",
    "شهي", "شهيه", "شهية", "وشهي", "وشهيه", "وشهية",
    "طازج", "طازجه", "طازجة", "وطازج", "وطازجه", "وطازجة",
    "سهل", "سهله", "سهلة", "وسهل", "وسهله", "وسهلة",
    "حلو", "حلوه", "حلوة", "وحلو", "وحلوه", "وحلوة",
    "طيب", "طيبه", "طيبة", "وطيب", "وطيبه", "وطيبة",
    "جميل", "جميله", "جميلة", "وجميل", "وجميله", "وجميلة",
    "كويس", "كويسه", "كويسة", "وكويس", "وكويسه", "وكويسة",
    "جديد", "جديده", "جديدة", "وجديد", "وجديده", "وجديدة",
    "بسيط", "بسيطه", "بسيطة", "وبسيط", "وبسيطه", "وبسيطة",
    "رخيص", "رخيصه", "رخيصة", "ورخيص", "ورخيصه", "ورخيصة",
    "اقتصادي", "اقتصاديه", "اقتصادية", "واقتصادي", "واقتصاديه", "واقتصادية",
    "مختلف", "مختلفه", "مختلفة", "ومختلف", "ومختلفه", "ومختلفة", "تغيير", "وتغيير",
    "دسم", "دسمه", "دسمة", "ودسم", "ودسمه", "ودسمة", "مش دسم", "مش دسمه", "مش دسمة",
    "تقيل", "تقيله", "تقيلة", "وتقيل", "وتقيله", "وتقيلة",
    "quick", "fast", "healthy", "fresh", "delicious", "easy", "good", "nice", "tasty", "simple",
    "cheap", "inexpensive", "affordable", "budget", "light", "heavy", "rich", "fatty", "different", "unique", "special"
}


class DomainGuard:
    def __init__(self):
        self.non_food_regex = re.compile("|".join(NON_FOOD_PATTERNS), re.IGNORECASE)
        self.out_catalog_regex = re.compile("|".join(OUT_OF_CATALOG_FOOD_PATTERNS), re.IGNORECASE)

    def inspect(self, raw_query: str, normalized_query: str, negation_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Evaluate query against domain boundaries.
        Returns:
            is_valid: bool
            decision: 'ACCEPT', 'REJECT_NON_FOOD', 'REJECT_OUT_OF_CATALOG', 'REJECT_CONTRADICTORY', 'REQUEST_CLARIFICATION'
            reason_ar: str
            reason_en: str
        """
        text = f"{raw_query} {normalized_query}".strip()

        # 0. Pure Negation / Exclusion check without alternative
        neg_info = negation_info
        if neg_info is None:
            from SILLA_NLP.preprocessing.query_preprocessor import parse_negation_intent
            neg_info = parse_negation_intent(raw_query)

        if neg_info.get("has_negation") and not neg_info.get("has_alternative"):
            ex_items = neg_info.get("excluded_items", [])
            ex_str = " أو ".join(ex_items) if ex_items else "مكون معين"
            ex_str_en = " or ".join(ex_items) if ex_items else "specified ingredient"
            return {
                "is_valid": False,
                "decision": "REQUEST_CLARIFICATION",
                "reason_ar": f"لقد طلبت وصفة بدون ({ex_str}). يرجى تحديد الصنف أو المكون البديل المفضل لديك (مثل الخضار، البقوليات، أو الدواجن).",
                "reason_en": f"You requested a recipe without ({ex_str_en}). Please specify your preferred alternative ingredient (such as vegetables, lentils, or poultry)."
            }
        
        # 1. Non-food products check
        if self.non_food_regex.search(text):
            return {
                "is_valid": False,
                "decision": "REJECT_NON_FOOD",
                "reason_ar": "الطلب خارج نطاق الطعام والطهي (منتجات وأجهزة غير غذائية).",
                "reason_en": "Out of domain: Non-food query detected."
            }

        # 2. Contradictory / Incompatible Culinary Concepts Check
        for dish_pat, incomp_pat, reason_ar, reason_en in CONFLICT_PATTERNS:
            if re.search(dish_pat, text, re.IGNORECASE) and re.search(incomp_pat, text, re.IGNORECASE):
                return {
                    "is_valid": False,
                    "decision": "REJECT_CONTRADICTORY",
                    "reason_ar": reason_ar,
                    "reason_en": reason_en
                }

        # 3. Out-of-catalog food check
        if self.out_catalog_regex.search(text):
            match = self.out_catalog_regex.search(text).group(0)
            return {
                "is_valid": False,
                "decision": "REJECT_OUT_OF_CATALOG",
                "reason_ar": f"صنف الطعام المطلوب ({match}) غير متوفر حالياً في كتالوج الوصفات المدعومة.",
                "reason_en": f"Out of catalog: Food category '{match}' is not supported in the recipe database."
            }

        # 4. Ambiguous / Generic query check (all tokens are ambiguous fillers or modifiers)
        from SILLA_NLP.preprocessing.query_preprocessor import STOP_WORDS
        norm_tokens = [t.lower() for t in normalized_query.split() if len(t) > 1]
        raw_tokens = [t.lower() for t in raw_query.split() if len(t) > 1]
        all_tokens = norm_tokens or raw_tokens
        if not all_tokens:
            return {
                "is_valid": False,
                "decision": "REQUEST_CLARIFICATION",
                "reason_ar": "الطلب غامض أو عام جداً. يرجى تحديد مكون أو صنف طعام تفضله.",
                "reason_en": "Query is too broad or ambiguous. Please specify a preferred ingredient or dish."
            }

        def _is_token_ambiguous(tok: str) -> bool:
            tok_norm = normalize_arabic(tok).lower()
            if tok_norm in AMBIGUOUS_TOKENS or tok_norm in GENERIC_MODIFIERS:
                return True
            stemmed = stem_arabic_token(tok_norm)
            if stemmed in AMBIGUOUS_TOKENS or stemmed in GENERIC_MODIFIERS:
                return True
            return False

        content_tokens = [t for t in all_tokens if t not in STOP_WORDS]
        tokens_to_check = content_tokens or all_tokens
        is_purely_ambiguous = all(_is_token_ambiguous(t) for t in tokens_to_check)
        if is_purely_ambiguous:
            return {
                "is_valid": False,
                "decision": "REQUEST_CLARIFICATION",
                "reason_ar": "الطلب غامض أو عام جداً. يرجى تحديد مكون أو صنف طعام تفضله.",
                "reason_en": "Query is too broad or ambiguous. Please specify a preferred ingredient or dish."
            }

        return {
            "is_valid": True,
            "decision": "ACCEPT",
            "reason_ar": "الاستعلام يقع ضمن نطاق الوصفات والطهي المعتمد.",
            "reason_en": "Query is within valid culinary scope."
        }
