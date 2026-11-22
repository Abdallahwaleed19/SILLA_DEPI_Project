"""
SILLA_NLP/preprocessing/query_preprocessor.py
============================================
Comprehensive Query Preprocessing Pipeline for Arabic, Egyptian Colloquial, and English queries.

Features:
- Pure-regex Arabic text normalization (tashkeel, tatweel, alef normalization, teh marbuta).
- Egyptian colloquial prefix and conversational filler stripping.
- Egyptian colloquial ingredient synonym mapping to canonical terms with proclitic support.
- Light Arabic stemming for definite article ('ال') and plural/feminine markers.
- Stop-word filtering for precise token overlap calculation.
"""

import re
import unicodedata
from typing import Dict, List, Set, Tuple, Any, Optional

# ---------------------------------------------------------------------------
# Character-level replacements
# ---------------------------------------------------------------------------
# Character-level replacements & Accent Stripping
# ---------------------------------------------------------------------------
def strip_accents(text: str) -> str:
    """Normalize unicode and strip combining diacritical marks (e.g. é -> e)."""
    if not isinstance(text, str):
        return ""
    nfkd = unicodedata.normalize("NFKD", text)
    return "".join(c for c in nfkd if not unicodedata.combining(c))

_ALEF_VARIANTS = re.compile(r"[أإآٱ]")
_DIACRITICS = re.compile(
    r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06DC\u06DF-\u06E4\u06E7-\u06E8\u06EA-\u06ED]"
)
_TATWEEL = re.compile(r"\u0640")
_ZERO_WIDTH = re.compile(r"[\u200B\u200C\u200D\u200E\u200F\uFEFF]")

# Conversational Prefixes & Intents to Strip (support both ة and ه)
CONVERSATIONAL_PREFIXES = [
    r"\bعايز[ةه]?\s+اعمل\b",
    r"\bعاوز[ةه]?\s+اعمل\b",
    r"\bعاوز[ةه]?\s+اطبخ\b",
    r"\bعايز[ةه]?\s+اطبخ\b",
    r"\bعايز[ةه]?\s+(?:اكل[ةه]|وجب[ةه]|وصف[ةه]|طبخ[ةه]|حاج[ةه])\s*(?:بـ?|في|من)?\b",
    r"\bعاوز[ةه]?\s+(?:اكل[ةه]|وجب[ةه]|وصف[ةه]|طبخ[ةه]|حاج[ةه])\s*(?:بـ?|في|من)?\b",
    r"\bوصف[ةه]\s*(?:بـ?|في|من|لـ|ال)?\b",
    r"\bاكل[ةه]\s*(?:بـ?|في|من|لـ|ال)?\b",
    r"\bوجب[ةه]\s*(?:بـ?|في|من|لـ|ال)?\b",
    r"\bطريق[ةه]\s+عمل\b",
    r"\bطريق[ةه]\s+تحضير\b",
    r"\bازاي\s+اعمل\b",
    r"\bازاي\s+اطبخ\b",
    r"\bنفسي\s+في\b",
    r"\bنفسي\s+اكل\b",
    r"\bطريق[ةه]\s+ال\b",
    r"\bكيفي[ةه]\s+عمل\b",
    r"\bاعمل[ل|ي]?\s*لي?\b",
    r"\bرشح\s*لي?\b",
    r"\bاقترح\s*لي?\b",
    r"\bسو[يى]\s*لي?\b",
    r"\bاطبخ\s*لي?\b",
    r"\bاقترح\s+علي[اى]\s+(?:وصف[ةه]|اكل[ةه]|طبخ[ةه])?\s*(?:مناسب[ةه])?\b",
    r"\bاقترح\s+(?:علين[اى]\s+)?(?:لي\s+)?(?:وصف[ةه]|اكل[ةه]|طبخ[ةه])\b",
    r"\bعندي\b",
    r"\bأ?قدر\s+أ?عمل\s+(?:بيهم\s+)?إ?يه\b",
    r"\bأ?عمل\s+(?:بيهم\s+)?إ?يه\b",
    r"\bhow\s+to\s+make\b",
    r"\bhow\s+to\s+cook\b",
    r"\bi\s+want\s+to\s+make\b",
    r"\bi\s+want\s+to\s+cook\b",
    r"\brecipe\s+for\b",
    r"\bi\s+want\s+(?:a\s+)?(?:quick\s+)?(?:meal|dish|recipe)\s+(?:with|of)?\b",
    r"\b(?:can|could|would)\s+you\s+(?:please\s+)?suggest\s+(?:something\s+|anything\s+|(?:an?\s+)?(?:recipe|dish|meal)\s+(?:with|for)?\b)?",
    r"\bsuggest\s+(?:an?\s+)?(?:recipe|dish|meal)\s+(?:with|for)?\b",
    r"\bi\s+need\s+(?:something\s+)?\b",
    r"\bi\s+want\s+something\s+\b",
]

# Colloquial Fillers & Modifiers (removes noise without losing intent)
COLLOQUIAL_FILLERS = [
    r"\bزي\s+المحلات\b",
    r"\bبتاع[ةه]?\s+زمان\b",
    r"\bعل[يى]\s+اصول[هة]\b",
    r"\bزي\s+المطاعم\b",
    r"\bبطريق[ةه]\s+سهل[ةه]\b",
    r"\bطعم\s+حكاي[ةه]\b",
    r"\bفي\s+البيت\b",
    r"\bمن\s+البيت\b",
    r"\bأ?قدر\s+أ?عمل\s+(?:بيهم\s+)?إ?يه\b",
    r"\bأ?عمل\s+(?:بيهم\s+)?إ?يه\b",
    r"\bمناسب[ةه]?\b",
    r"\bو?خلاص\b"
]

# Egyptian Colloquial to Canonical Ingredient Mapping (with proclitic support: بـ, وـ, كـ, لـ, الـ)
EGYPTIAN_SYNONYM_RULES = [
    # Proteins (supporting proclitics and ensuring base noun is present for TF-IDF)
    (r"\b([وبك]?ل?)(?:ال)?لحم[ةه]?\s+(?:ال)?مفروم[ةه]?\b", r"\1لحم بقري مفروم كفتة حواوشي"),
    (r"\b([وبك]?ل?)(?:ال)?مفروم[ةه]\b", r"\1مفروم"),
    (r"\b([وبك]?ل?)ال(?:فراخ|فرخ[ةه])\b", r"\1الدجاج دجاج"),
    (r"\b([وبك]?ل?)(?:فراخ|فرخ[ةه])\b", r"\1دجاج"),
    (r"\b([وبك]?ل?)اللحم[ةه]\b", r"\1اللحم لحم"),
    (r"\b([وبك]?ل?)لحم[ةه]\b", r"\1لحم"),
    (r"\b([وبك]?ل?)(?:ال)?بتلو\b", r"\1لحم بقري"),
    (r"\b([وبك]?ل?)(?:ال)?لي[ةه]\s+(?:ال)?ضاني\b", r"\1دهن لية ضاني"),
    (r"\b([وبك]?ل?)(?:ال)?لي[ةه]\b", r"\1دهن لية ضاني"),
    # Vegetables & Seasonings
    (r"\b([وبك]?ل?)ال(?:خضار|خضروات)\b", r"\1الخضار خضار"),
    (r"\b([وبك]?ل?)(?:خضار|خضروات)\b", r"\1خضار"),
    (r"\b([وبك]?ل?)ال(?:عدس)\b", r"\1العدس عدس"),
    (r"\b([وبك]?ل?)(?:عدس)\b", r"\1عدس"),
    (r"\b([وبك]?ل?)ال(?:بطاطس)\b", r"\1البطاطس بطاطس"),
    (r"\b([وبك]?ل?)(?:بطاطس)\b", r"\1بطاطس"),
    (r"\b([وبك]?ل?)ال(?:طماطم)\b", r"\1الطماطم طماطم"),
    (r"\b([وبك]?ل?)(?:طماطم)\b", r"\1طماطم"),
    (r"\b([وبك]?ل?)ال(?:بصل)\b", r"\1البصل بصل"),
    (r"\b([وبك]?ل?)(?:بصل)\b", r"\1بصل"),
    (r"\b([وبك]?ل?)ال(?:دجاج)\b", r"\1الدجاج دجاج"),
    (r"\b([وبك]?ل?)(?:دجاج)\b", r"\1دجاج"),
    (r"\b([وبك]?ل?)ال(?:قوط|اوط)[ةه]\b", r"\1الطماطم طماطم"),
    (r"\b([وبك]?ل?)(?:قوط|اوط)[ةه]\b", r"\1طماطم"),
    (r"\b([وبك]?ل?)التوم[ةه]?\b", r"\1الثوم ثوم"),
    (r"\b([وبك]?ل?)توم[ةه]?\b", r"\1ثوم"),
    (r"\b([وبك]?ل?)(?:ال)?شبت\b", r"\1شبت"),
    (r"\b([وبك]?ل?)(?:ال)?بقدونس\b", r"\1بقدونس"),
    (r"\b([وبك]?ل?)(?:ال)?كزبر[ةه]\b", r"\1كزبرة"),
    (r"\b([وبك]?ل?)(?:ال)?لمون\b", r"\1ليمون"),
    (r"\b([وبك]?ل?)(?:ال)?شط[ةه]\b", r"\1شطة حمراء"),
    # Grains & Breads
    (r"\b([وبك]?ل?)الرز\b", r"\1الارز ارز"),
    (r"\b([وبك]?ل?)رز\b", r"\1ارز"),
    (r"\b([وبك]?ل?)(?:ال)?عيش\s+(?:ال)?بلدي\b", r"\1خبز بلدي"),
    (r"\b([وبك]?ل?)(?:ال)?عيش\b", r"\1خبز"),
    (r"\b([وبك]?ل?)(?:ال)?مكرون[ةه]\b", r"\1مكرونة"),
    (r"\b([وبك]?ل?)(?:ال)?شرب[ةه]\b", r"\1شوربة"),
    (r"\b([وبك]?ل?)(?:ال)?صلص[ةه]\b", r"\1صلصة"),
    # Dairy & Sauces
    (r"\b([وبك]?ل?)(?:ال)?لبن\b", r"\1حليب"),
    (r"\b([وبك]?ل?)(?:ال)?جبن[ةه]\b", r"\1جبن"),
    (r"\b([وبك]?ل?)(?:ال)?سمن[ةه]\b", r"\1سمن"),
    (r"\b([وبك]?ل?)(?:ال)?بشميل\b", r"\1بشاميل"),
]

# English synonym mapping
ENGLISH_SYNONYM_RULES = [
    (r"\bpotatoes\b", "potato"),
    (r"\btomatoes\b", "tomato"),
    (r"\bonions\b", "onion"),
    (r"\beggs\b", "egg"),
    (r"\bpeppers\b", "pepper"),
    (r"\bveggies\b", "vegetables"),
    (r"\bveggie\b", "vegetable"),
    (r"\bspaghetti\b", "pasta"),
    (r"\bpenne\b", "penne pasta"),
    (r"\bfava\b", "fava beans"),
]

STOP_WORDS = {
    "على", "علي", "في", "من", "مع", "زي", "بتاع", "بتاعة", "بتاعه", "عايز", "عاوز", "طريقة", "عمل", "تحضير",
    "ازاي", "نفسي", "هو", "هي", "عن", "الى", "الي", "إلى", "كل", "او", "أو", "ثم",
    "وصفه", "وصفة", "وصفات", "ممكن", "خفيف", "خفيفة", "خفيفه", "عشا", "عشاء",
    "عندي", "اقدر", "أقدر", "ايه", "إيه", "بيهم", "فيه", "فيها", "عليا", "علينا",
    "لي", "ليا", "لينا", "لنا", "لك", "لكم", "مناسب", "مناسبة", "مناسبه", "اقترح", "اقترحي",
    "with", "and", "in", "the", "for", "a", "an", "of", "to", "at", "by",
    "how", "make", "cook", "recipe", "want", "meal", "dish", "dishes", "meals", "something", "anything", "suggest", "give", "need", "can", "could", "would", "you", "please", "i", "me"
}

# Arabic Nouns & Adjectives whose root begins with ב/و/ف/ك/ل - NEVER strip initial consonant!
ROOT_INITIAL_EXCEPTIONS = {
    # Nouns & adjectives starting with root و
    "وصفة", "وصفه", "وصفات", "ورق", "ويكة", "ويكه", "وجبة", "وجبه", "وجبات", "وز",
    # Nouns & adjectives starting with root ب
    "بطاطس", "بقدونس", "بشاميل", "بصل", "بامية", "باميه", "برتقال", "بيض", "بندق", "باذنجان", "بقري", "بتلو", "بهارات", "برجر",
    # Nouns & adjectives starting with root ف
    "فلفل", "فراخ", "فرخة", "فرخه", "فاصوليا", "فستق", "فطر", "فتة", "فته", "فول",
    # Nouns & adjectives starting with root ك
    "كوسة", "كوسه", "كمون", "كزبرة", "كزبره", "كرفس", "كرنب", "كركم", "كاري", "كفتة", "كفته", "كشري",
    # Nouns & adjectives starting with root ل
    "لحم", "لحمة", "لحمه", "ليمون", "لوبيا", "لبن", "لية", "ليه"
}


def normalize_arabic(text: str) -> str:
    """Normalize Arabic text: diacritics, tatweel, alef variants, teh marbuta, and accents."""
    if not isinstance(text, str):
        return ""
    text = strip_accents(unicodedata.normalize("NFKC", text))
    text = _ZERO_WIDTH.sub("", text)
    text = _DIACRITICS.sub("", text)
    text = _TATWEEL.sub("", text)
    text = _ALEF_VARIANTS.sub("ا", text)
    text = re.sub(r"ة\b", "ه", text)
    text = re.sub(r"ى\b", "ي", text)
    return text


def stem_arabic_token(word: str) -> str:
    """
    Morphologically safe light Arabic stemmer:
    - Normalizes characters and strips accents.
    - Strips compound proclitic prefixes (بالـ, والـ, فالـ, كالـ, وللـ) safely.
    - Strips definite articles (للـ, الـ) safely.
    - Strips coordinating conjunction 'و' unless the word is a known root starting with 'و'.
    - Strips single proclitic prefixes (بـ, فـ, كـ, لـ) ONLY if word is not in ROOT_INITIAL_EXCEPTIONS.
    """
    w = strip_accents(normalize_arabic(word))
    if len(w) >= 5 and (w.startswith("بال") or w.startswith("وال") or w.startswith("فال") or w.startswith("كال") or w.startswith("ولل")):
        w = w[3:]
    elif len(w) >= 4 and (w.startswith("لل") or w.startswith("ال")):
        w = w[2:]
    elif len(w) >= 4 and w.startswith("و") and w not in ROOT_INITIAL_EXCEPTIONS:
        w = w[1:]
    elif len(w) > 4 and w[0] in {"ب", "ف", "ك", "ل"} and w not in ROOT_INITIAL_EXCEPTIONS:
        w = w[1:]
    return w


def extract_content_stems(text: str) -> Set[str]:
    """Extract informative, stemmed tokens excluding common stop-words."""
    norm = normalize_arabic(text)
    words = [w for w in re.split(r"[^\w]+", norm) if w and w.lower() not in STOP_WORDS]
    stems = set()
    for w in words:
        s = stem_arabic_token(w)
        if len(s) > 1:
            stems.add(s.lower())
            if s == "فراخ":
                stems.add("دجاج")
            elif s in {"قوطه", "اوطه"}:
                stems.add("طماطم")
            elif s in {"مفروم", "مفرومه"}:
                stems.add("مفروم")
                stems.add("beef")
            elif s in {"لحم", "لحمه", "لحوم"}:
                stems.add("لحم")
                stems.add("meat")
                stems.add("beef")
            elif s == "مكرونه":
                stems.add("pasta")
                stems.add("macaroni")
    en_words = [strip_accents(w).lower() for w in re.split(r"[^a-zA-Z]+", text) if len(w) > 2 and w.lower() not in STOP_WORDS]
    for w in en_words:
        stems.add(w)
        if w.endswith("es") and len(w) > 4:
            if w == "tomatoes": stems.add("tomato")
            elif w == "potatoes": stems.add("potato")
        elif w.endswith("s") and len(w) > 3 and not w.endswith("ss"):
            stems.add(w[:-1])
        if w in {"pasta", "macaroni"}:
            stems.add("pasta")
            stems.add("macaroni")
    return stems


def clean_query_text(query: str) -> str:
    """Strip conversational prefixes, colloquial fillers, and normalize synonyms."""
    if not query:
        return ""
    
    q = query.strip()
    
    # 1. Normalize alef & basic characters first
    q = normalize_arabic(q)
    
    # 2. Strip conversational prefixes
    for pat in CONVERSATIONAL_PREFIXES:
        q = re.sub(pat, " ", q, flags=re.IGNORECASE)
        
    # 3. Strip colloquial fillers
    for pat in COLLOQUIAL_FILLERS:
        q = re.sub(pat, " ", q, flags=re.IGNORECASE)
        
    # 4. Map colloquial synonyms
    for pat, rep in EGYPTIAN_SYNONYM_RULES:
        q = re.sub(pat, rep, q, flags=re.IGNORECASE)
        
    for pat, rep in ENGLISH_SYNONYM_RULES:
        q = re.sub(pat, rep, q, flags=re.IGNORECASE)
        
    # 5. Clean punctuation and collapse whitespace
    q = re.sub(r"[^\w\s-]", " ", q)
    q = re.sub(r"\s+", " ", q).strip()
    return q


# ---------------------------------------------------------------------------
# Negation & Exclusion Handling
# ---------------------------------------------------------------------------
NEGATION_PATTERNS = [
    # Arabic: من غير, بدون, خالي من, بلا
    r"\bمن\s+غير\b",
    r"\bبدون\b",
    r"\bخال(?:ي|ية|يه)\s+من\b",
    r"\bبلا\b",
    # English: without, free of, free from, no
    r"\bwithout\b",
    r"\bfree\s+(?:of|from)\b",
    r"\bno\b",
]

NEGATION_SYNONYM_EXPANSIONS = {
    "لحم": {"لحم", "لحمه", "meat", "beef", "بتلو", "ضان", "ضاني", "مفروم", "مفرومة"},
    "لحمه": {"لحم", "لحمه", "meat", "beef", "بتلو", "ضان", "ضاني", "مفروم", "مفرومة"},
    "لحوم": {"لحم", "لحمه", "لحوم", "meat", "beef", "دجاج", "فراخ", "chicken", "سمك", "fish", "بتلو", "ضان", "ضاني", "مفروم", "مفرومة"},
    "meat": {"لحم", "لحمه", "meat", "beef", "بتلو", "ضان", "ضاني", "مفروم", "مفرومة"},
    "beef": {"لحم", "لحمه", "meat", "beef", "بتلو", "ضان", "ضاني", "مفروم", "مفرومة"},
    "دجاج": {"دجاج", "فراخ", "chicken", "اوراك", "صدور"},
    "فراخ": {"دجاج", "فراخ", "chicken", "اوراك", "صدور"},
    "chicken": {"دجاج", "فراخ", "chicken", "اوراك", "صدور"},
    "سمك": {"سمك", "fish", "seafood", "جمبري", "تونة", "تونه", "سالمون"},
    "fish": {"سمك", "fish", "seafood", "جمبري", "تونة", "تونه", "سالمون"},
    "seafood": {"سمك", "fish", "seafood", "جمبري", "تونة", "تونه", "سالمون"},
    "لبن": {"لبن", "حليب", "milk", "كريمة", "كريمه", "cream", "قشطة", "قشطه"},
    "حليب": {"لبن", "حليب", "milk", "كريمة", "كريمه", "cream", "قشطة", "قشطه"},
    "milk": {"لبن", "حليب", "milk", "كريمة", "كريمه", "cream", "قشطة", "قشطه"},
    "جبن": {"جبن", "جبنة", "جبنه", "cheese", "موزاريلا", "موتزاريلا", "شيدر", "رومي", "بارميزان", "قريش", "mozzarella", "cheddar", "parmesan"},
    "جبنة": {"جبن", "جبنة", "جبنه", "cheese", "موزاريلا", "موتزاريلا", "شيدر", "رومي", "بارميزان", "قريش", "mozzarella", "cheddar", "parmesan"},
    "cheese": {"جبن", "جبنة", "جبنه", "cheese", "mozzarella", "cheddar", "parmesan", "موزاريلا", "موتزاريلا", "شيدر", "رومي", "بارميزان", "قريش"},
    "طماطم": {"طماطم", "tomato", "tomatoes", "صلصة", "صلصه", "معجون طماطم"},
    "tomato": {"طماطم", "tomato", "tomatoes", "صلصة", "صلصه", "معجون طماطم"},
    "tomatoes": {"طماطم", "tomato", "tomatoes", "صلصة", "صلصه", "معجون طماطم"},
}

GENERIC_FOOD_FILTER = {
    "سهل", "سهله", "سهلة", "سريع", "سريعه", "سريعة", "صحي", "صحيه", "صحية",
    "حلو", "حلوه", "حلوة", "ممكن", "عايز", "عاوز", "اريد", "محتاج", "وصفه", "وصفة", "اكله", "أكلة", "اكلة", "وجبه", "وجبة",
    "حاجه", "حاجة", "طريقة", "عمل", "اكل", "طعام", "شيء", "شئ", "نفسي", "في", "مع", "من", "اي", "اية", "ايه",
    "نوع", "انواع", "اي نوع", "أي نوع",
    "اقترح", "اقترحي", "اقترحلي", "اقترحيلي", "رشحلي", "سويلي", "طبخلي", "اعملي", "اعمللي", "عايزة", "عاوزة",
    "عندي", "اقدر", "أقدر", "بيهم", "فيه", "فيها", "عليا", "علينا", "مناسب", "مناسبة", "مناسبه",
    "quick", "fast", "healthy", "fresh", "delicious", "easy", "good", "nice", "tasty", "simple", "recipe", "want", "dish", "meal", "something", "can", "you", "suggest", "give", "need"
}

def parse_negation_intent(raw_query: str) -> Dict[str, Any]:
    """
    Detect negation & exclusion patterns in Arabic and English queries.
    Supports single and compound negations (e.g. 'من غير لحمة ولا فراخ', 'بدون لبن أو جبنة', 'without meat nor chicken').
    Correctly identifies whether an alternative was provided.
    """
    q_raw = raw_query.strip()
    trigger_m = None
    for pat in NEGATION_PATTERNS:
        m = re.search(pat, q_raw, re.IGNORECASE)
        if m:
            trigger_m = m
            break

    if not trigger_m:
        return {
            "has_negation": False,
            "excluded_items": [],
            "excluded_stems": set(),
            "positive_query": q_raw,
            "has_alternative": True,
            "remaining_food_stems": set()
        }

    before_neg = q_raw[:trigger_m.start()].strip()
    after_neg = q_raw[trigger_m.end():].strip()

    # Detect positive resumption boundary: e.g. "بالخضار", "بالعدس", "مع خضار", "with vegetables"
    pos_boundary_m = re.search(r"\s+(?:بال[^\s]+|مع\s+[^\s]+|في\s+[^\s]+|with\s+[^\s]+)", after_neg, re.IGNORECASE)
    if pos_boundary_m:
        neg_clause = after_neg[:pos_boundary_m.start()].strip()
        pos_clause = after_neg[pos_boundary_m.start():].strip()
    else:
        neg_clause = after_neg
        pos_clause = ""

    # Split compound negative clause into individual excluded items
    raw_excluded = re.split(r"\s+(?:ولا|أو|او|و|nor|or|and)\s+|,\s*", neg_clause, flags=re.IGNORECASE)
    excluded_items = []
    excluded_stems = set()

    for item in raw_excluded:
        cleaned_ex = re.sub(r"\b(?:أي|اي|اي\s+نوع\s+من|أي\s+نوع\s+من|أي\s+نوع|اي\s+نوع|any)\s+", "", item.strip())
        cleaned_ex = cleaned_ex.strip(" .،,")
        if cleaned_ex:
            excluded_items.append(cleaned_ex)
            raw_stems = extract_content_stems(cleaned_ex)
            for s in raw_stems:
                excluded_stems.add(s)
                if s in NEGATION_SYNONYM_EXPANSIONS:
                    excluded_stems.update(NEGATION_SYNONYM_EXPANSIONS[s])

    positive_query = f"{before_neg} {pos_clause}".strip()
    has_negation = len(excluded_items) > 0

    pos_stems = extract_content_stems(positive_query)
    remaining_food = {s for s in pos_stems if s not in GENERIC_FOOD_FILTER and len(s) > 1}
    has_alternative = len(remaining_food) > 0

    return {
        "has_negation": has_negation,
        "excluded_items": excluded_items,
        "excluded_stems": excluded_stems,
        "positive_query": positive_query,
        "has_alternative": has_alternative,
        "remaining_food_stems": remaining_food
    }


def preprocess_query_bundle(raw_query: str) -> Dict[str, any]:
    """
    Produce structured query representations:
    - raw_query: original text
    - normalized_query: cleaned and synonym-expanded
    - tokens: list of clean tokens
    - content_stems: set of informative stems
    - language_hint: 'ar', 'en', or 'mixed'
    - negation_info: negation/exclusion metadata
    """
    raw_query = raw_query.strip()
    cleaned = clean_query_text(raw_query)
    neg_info = parse_negation_intent(raw_query)
    
    has_ar = bool(re.search(r"[\u0600-\u06FF]", raw_query))
    has_en = bool(re.search(r"[a-zA-Z]", raw_query))
    
    if has_ar and has_en:
        lang = "mixed"
    elif has_ar:
        lang = "ar"
    elif has_en:
        lang = "en"
    else:
        lang = "other"
        
    tokens = [t for t in cleaned.split() if len(t) > 1]
    stems = extract_content_stems(cleaned)
    
    return {
        "raw_query": raw_query,
        "normalized_query": cleaned,
        "tokens": tokens,
        "content_stems": stems,
        "language_hint": lang,
        "negation_info": neg_info
    }
