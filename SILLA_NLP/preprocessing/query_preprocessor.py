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
from typing import Dict, List, Set, Tuple

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
    r"\bhow\s+to\s+make\b",
    r"\bhow\s+to\s+cook\b",
    r"\bi\s+want\s+to\s+make\b",
    r"\bi\s+want\s+to\s+cook\b",
    r"\brecipe\s+for\b"
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
    r"\bو?خلاص\b"
]

# Egyptian Colloquial to Canonical Ingredient Mapping (with proclitic support: بـ, وـ, كـ, لـ, الـ)
EGYPTIAN_SYNONYM_RULES = [
    # Proteins (supporting proclitics and ensuring base noun is present for TF-IDF)
    (r"\b([وبك]?ل?)ال(?:فراخ|فرخ[ةه])\b", r"\1الدجاج دجاج"),
    (r"\b([وبك]?ل?)(?:فراخ|فرخ[ةه])\b", r"\1دجاج"),
    (r"\b([وبك]?ل?)اللحم[ةه]\b", r"\1اللحم لحم"),
    (r"\b([وبك]?ل?)لحم[ةه]\b", r"\1لحم"),
    (r"\b([وبك]?ل?)(?:ال)?بتلو\b", r"\1لحم بقري"),
    (r"\b([وبك]?ل?)(?:ال)?لي[ةه]\s+(?:ال)?ضاني\b", r"\1دهن لية ضاني"),
    (r"\b([وبك]?ل?)(?:ال)?لي[ةه]\b", r"\1دهن لية ضاني"),
    # Vegetables & Seasonings
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
    (r"\bveggies\b", "vegetables"),
    (r"\bveggie\b", "vegetable"),
    (r"\bspaghetti\b", "pasta"),
    (r"\bpenne\b", "penne pasta"),
    (r"\bfava\b", "fava beans"),
]

STOP_WORDS = {
    "على", "علي", "في", "من", "مع", "زي", "بتاع", "عايز", "طريقة", "عمل", "تحضير",
    "ازاي", "نفسي", "هو", "هي", "عن", "الى", "الي", "إلى", "كل", "او", "أو", "ثم",
    "with", "and", "in", "the", "for", "a", "an", "of", "to", "at", "by",
    "how", "make", "cook", "recipe", "want"
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
    Light Arabic stemmer:
    - Normalizes characters and strips accents.
    - Strips proclitic prefixes (بالـ, فالـ, كالـ, وللـ, للـ, الـ, بـ, وـ, فـ, كـ, لـ) safely.
    """
    w = strip_accents(normalize_arabic(word))
    if len(w) > 5 and (w.startswith("بال") or w.startswith("فال") or w.startswith("كال") or w.startswith("ولل")):
        w = w[3:]
    elif len(w) > 4 and (w.startswith("لل") or w.startswith("ال")):
        w = w[2:]
    elif len(w) > 4 and w[0] in {"ب", "و", "ف", "ك", "ل"}:
        w = w[1:]
    return w


def extract_content_stems(text: str) -> Set[str]:
    """Extract informative, stemmed tokens excluding common stop-words."""
    norm = normalize_arabic(text)
    words = [w for w in re.split(r"[^\w]+", norm) if w and w not in STOP_WORDS]
    stems = set()
    for w in words:
        s = stem_arabic_token(w)
        if len(s) > 1:
            stems.add(s.lower())
            if s == "فراخ":
                stems.add("دجاج")
            elif s in {"قوطه", "اوطه"}:
                stems.add("طماطم")
            elif s == "مكرونه":
                stems.add("pasta")
                stems.add("macaroni")
    en_words = [strip_accents(w).lower() for w in re.split(r"[^a-zA-Z]+", text) if len(w) > 2 and w.lower() not in STOP_WORDS]
    for w in en_words:
        stems.add(w)
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


def preprocess_query_bundle(raw_query: str) -> Dict[str, any]:
    """
    Produce structured query representations:
    - raw_query: original text
    - normalized_query: cleaned and synonym-expanded
    - tokens: list of clean tokens
    - content_stems: set of informative stems
    - language_hint: 'ar', 'en', or 'mixed'
    """
    raw_query = raw_query.strip()
    cleaned = clean_query_text(raw_query)
    
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
        "language_hint": lang
    }
