"""
SILLA_NLP
=========
Smart Recipe Discovery & NLP Module for SILLA Project (DEPI Egypt).
"""

from SILLA_NLP.api import SillaRecipeMatcher, match_recipe
from SILLA_NLP.matching.hybrid_engine import HybridEngine
from SILLA_NLP.preprocessing.query_preprocessor import (
    clean_query_text,
    normalize_arabic,
    preprocess_query_bundle
)
from SILLA_NLP.intent_guard.domain_guard import DomainGuard

__all__ = [
    "SillaRecipeMatcher",
    "match_recipe",
    "HybridEngine",
    "DomainGuard",
    "clean_query_text",
    "normalize_arabic",
    "preprocess_query_bundle"
]
