"""
SILLA_Recommendation/config.py
==============================
Configuration, database paths, and unit conversion standards for SILLA Recommendation & Cost Engine.
"""

from pathlib import Path

# Paths
MODULE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = MODULE_ROOT.parent
DATA_ENG_ROOT = PROJECT_ROOT / "SILLA_Data_Engineering"

# Database path (Always uses silla_staging.db during development & validation)
STAGING_DB_PATH = DATA_ENG_ROOT / "database" / "silla_staging.db"
PRODUCTION_DB_PATH = DATA_ENG_ROOT / "database" / "silla.db"
DB_PATH = STAGING_DB_PATH

# Output Reports
REPORT_PATH = DATA_ENG_ROOT / "data" / "processed" / "recommendation_cost_validation_report.json"

# Recommendation Hyperparameters
NLP_SCORE_WEIGHT = 0.70         # Weight for semantic/lexical intent match
AVAILABILITY_WEIGHT = 0.30      # Weight for ingredient product coverage
CORE_RECIPE_BOOST = 0.05        # Modest priority boost for authentic core recipes (R0001-R0016)
MIN_COVERAGE_THRESHOLD = 0.30   # Minimum ingredient price coverage to consider viable

# Authentic Core Egyptian Recipes
CORE_EGYPTIAN_RECIPE_IDS = {
    f"R{i:04d}" for i in range(1, 17)
}

# Documented Unit Conversion Registry (Physics & Culinary Standards)
# Maps (source_unit, target_unit) to multiplicative factor: target = source * factor
STANDARD_UNIT_CONVERSIONS = {
    # Volume conversions
    ("tsp", "ml"): 5.0,
    ("tbsp", "ml"): 15.0,
    ("cup", "ml"): 240.0,
    ("l", "ml"): 1000.0,
    ("ml", "ml"): 1.0,
    ("ml", "l"): 0.001,

    # Mass conversions
    ("g", "g"): 1.0,
    ("kg", "g"): 1000.0,
    ("g", "kg"): 0.001,

    # Documented Culinary volume-to-mass (liquids, pastes, ground spices)
    ("tsp", "g"): 5.0,       # 1 tsp ground spice/salt ~ 5.0g
    ("tbsp", "g"): 15.0,     # 1 tbsp tomato paste/flour/butter ~ 15.0g
    ("cup", "g"): 200.0,     # 1 standard culinary cup ~ 200g

    # Count/piece conversions
    ("clove", "g"): 4.0,     # 1 garlic clove ~ 4.0g (culinary standard: 3-5g)
    ("bunch", "bunch"): 1.0,
    ("bunch", "g"): 50.0,    # 1 standard fresh herb bunch (dill, parsley) ~ 50g
    ("piece", "piece"): 1.0,
}

# Produce item piece-to-gram standard weight in Egyptian supermarkets
PRODUCE_PIECE_WEIGHT_G = {
    "ING0071": 125.0,  # Yellow Onion (بصل أصفر) ~ 125g
    "ING0053": 150.0,  # Potato (بطاطس) ~ 150g
    "ING0016": 100.0,  # Carrot (جزر) ~ 100g
    "ING0046": 60.0,   # Lemon (ليمون) ~ 60g
    "ING0060": 60.0,   # Lemon alias
    "ING0056": 120.0,  # Tomato (طماطم حمراء) ~ 120g
    "ING0041": 150.0,  # Bell pepper (فلفل رومي) ~ 150g
    "ING0008": 250.0,  # Eggplant (باذنجان رومي) ~ 250g
    "ING0028": 60.0,   # Whole Egg (بيضة) ~ 60g
}
