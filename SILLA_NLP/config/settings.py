"""
SILLA_NLP/config/settings.py
============================
Configuration settings, database paths, and model hyperparameters for SILLA NLP Engine.
"""

from pathlib import Path

# Paths
MODULE_ROOT = Path(__file__).resolve().parent.parent
PROJECT_ROOT = MODULE_ROOT.parent
DATA_ENG_ROOT = PROJECT_ROOT / "SILLA_Data_Engineering"

# Database path (Always uses silla_staging.db during NLP development & benchmark)
STAGING_DB_PATH = DATA_ENG_ROOT / "database" / "silla_staging.db"
PRODUCTION_DB_PATH = DATA_ENG_ROOT / "database" / "silla.db"
DB_PATH = STAGING_DB_PATH

# Output Reports
BENCHMARK_REPORT_PATH = DATA_ENG_ROOT / "data" / "processed" / "hybrid_nlp_benchmark_report.json"

# Models and Vectorizer Settings
ST_MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
EMBEDDING_DIM = 384

# Hybrid Matching Hyperparameters (Tuned on Validation Set)
DEFAULT_DENSE_WEIGHT = 0.55       # alpha (Sentence Transformers)
DEFAULT_SPARSE_WEIGHT = 0.45      # 1 - alpha (TF-IDF)
CORE_RECIPE_BOOST = 0.06          # Prioritizes R0001-R0016 without hiding generated recipes
EXACT_TITLE_BONUS = 0.15          # Confidence bonus for exact recipe title matches
REJECTION_THRESHOLD = 0.18        # Tau: below this, queries are safely rejected
AMBIGUITY_THRESHOLD = 0.28        # Below this, queries trigger clarification requests

# Logging
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
