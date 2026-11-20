"""
SILLA_Data_Science/data_loader.py
=================================
Loads the SILLA catalogue from the Data Engineering SQLite database and builds a
single analysis-ready table with one row per recipe:

- recipe metadata (category, cuisine, servings, times, difficulty)
- recipe "family" (style variants such as "Koshari (Cairo Street Style)" share
  the exact ingredient list with "Koshari", so they are grouped together)
- dietary flags derived from ingredient tags (vegan / vegetarian / pescatarian)
- cost per serving, re-using the team's CostCalculator (SILLA_Recommendation),
  plus an *estimated* full cost where missing ingredient prices are imputed
  from the median unit price of the ingredient's category.

Owner: Amr Badr — Data Science & Recommendation.
"""

from __future__ import annotations

import importlib
import re
import sqlite3
import sys
import types
from functools import lru_cache
from pathlib import Path
from typing import Dict, Optional

import numpy as np
import pandas as pd

MODULE_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = MODULE_ROOT.parent
DB_PATH = PROJECT_ROOT / "SILLA_Data_Engineering" / "database" / "silla_staging.db"
REPORTS_DIR = MODULE_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"

# Style suffixes the data pipeline appended to create recipe variants. A variant has
# exactly the same ingredients and quantities as its base recipe.
STYLE_SUFFIXES = (
    "Cairo Street Style",
    "Alexandrian Coastal Style",
    "Upper Egyptian Sa'Eedi Style",
    "Country Rural Style",
    "Spicy Hot Chilli Glazed",
    "Oven-Baked Clay Tagine",
)
_STYLE_RE = re.compile(r"\s*\((?:" + "|".join(re.escape(s) for s in STYLE_SUFFIXES) + r")\)\s*$")

DIFFICULTY_ORDER = {"Easy": 0, "Medium": 1, "Hard": 2}

# The shared CostCalculator converts "piece" -> grams with a 100 g default for any
# ingredient not in its produce table (whose IDs do not match the current
# ingredients table). For whole spices that turns 4 cardamom pods into 400 g
# (≈600 EGP). These realistic per-piece weights are applied on top of the
# calculator's output in this module only.
PIECE_WEIGHT_CORRECTIONS_G = {
    "ING0022": 0.2,   # Cardamom pod
    "ING0005": 0.2,   # Bay leaf
    "ING0032": 0.1,   # Clove (spice)
    "ING0030": 3.0,   # Cinnamon stick
    "ING0077": 0.1,   # Mastic gum tear
    "ING0044": 60.0,  # Egg
}


# --------------------------------------------------------------------------- #
# Raw tables
# --------------------------------------------------------------------------- #
def load_tables(db_path: Path = DB_PATH) -> Dict[str, pd.DataFrame]:
    """Read the main tables from the SILLA database."""
    db_path = Path(db_path)
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found: {db_path}")
    with sqlite3.connect(db_path) as conn:
        names = ["recipes", "recipe_ingredients", "ingredients", "products", "stores"]
        return {n: pd.read_sql(f"SELECT * FROM {n}", conn) for n in names}


def recipe_family(name_en: str) -> str:
    """'Koshari (Cairo Street Style)' -> 'Koshari'. Other parentheses are kept."""
    return _STYLE_RE.sub("", str(name_en)).strip()


# --------------------------------------------------------------------------- #
# Cost calculation (re-uses the team's CostCalculator)
# --------------------------------------------------------------------------- #
def _import_cost_calculator():
    """
    Import SILLA_Recommendation.cost_calculator without triggering the package
    __init__ (which imports the NLP stack and needs `fastembed`). The cost
    calculator itself only depends on SILLA_Recommendation.config.
    """
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    try:
        return importlib.import_module("SILLA_Recommendation.cost_calculator")
    except ImportError:
        for mod in [m for m in sys.modules if m.startswith("SILLA_Recommendation")]:
            del sys.modules[mod]
        pkg = types.ModuleType("SILLA_Recommendation")
        pkg.__path__ = [str(PROJECT_ROOT / "SILLA_Recommendation")]
        sys.modules["SILLA_Recommendation"] = pkg
        return importlib.import_module("SILLA_Recommendation.cost_calculator")


def category_unit_prices(products: pd.DataFrame, ingredients: pd.DataFrame) -> pd.Series:
    """Median price per gram (ml treated as g) for each ingredient category."""
    p = products[products["package_unit"].isin(["g", "ml"])].copy()
    p["egp_per_g"] = p["price_egp"] / p["package_size"]
    p = p.merge(ingredients[["ingredient_id", "category"]], on="ingredient_id",
                suffixes=("_product", ""))
    s = p.groupby("category")["egp_per_g"].median()
    s.loc["__global__"] = p["egp_per_g"].median()
    return s


def compute_recipe_costs(db_path: Path = DB_PATH, tables: Optional[Dict[str, pd.DataFrame]] = None) -> pd.DataFrame:
    """
    Cost per recipe across all stores (cheapest unit price per ingredient).

    Returns columns:
      calculator_cost_egp   raw net cost from the shared CostCalculator
      priced_cost_egp       same, after the per-piece weight corrections above
      imputed_cost_egp      estimated cost of ingredients with no product
      price_completeness    share of ingredients with a real price
      est_cost_egp          priced + imputed (used for analysis/recommendation)
    """
    tables = tables or load_tables(db_path)
    cc_mod = _import_cost_calculator()
    calc = cc_mod.CostCalculator(Path(db_path))
    conv = cc_mod.UnitConverter
    ing_cat = tables["ingredients"].set_index("ingredient_id")["category"]
    cat_price = category_unit_prices(tables["products"], tables["ingredients"])

    rows = []
    for rid in tables["recipes"]["recipe_id"]:
        res = calc.calculate_recipe_cost(rid)
        priced = res["net_recipe_cost_egp"]
        corrected_items = 0
        for item in res["priced_ingredients"]:
            w = PIECE_WEIGHT_CORRECTIONS_G.get(item["ingredient_id"])
            prod = item["matched_product"]
            if w and item["required_unit"] == "piece" and prod["package_unit"] == "g":
                new_cost = item["required_quantity"] * w / prod["package_size"] * prod["price_egp"]
                priced += new_cost - item["pro_rata_cost_egp"]
                corrected_items += 1
        imputed = 0.0
        for item in res["unpriced_ingredients"]:
            unit = "ml" if item["required_unit"] == "ml" else item["required_unit"]
            grams, _ = conv.convert(item["required_quantity"], unit,
                                    "ml" if unit == "ml" else "g", item["ingredient_id"])
            if unit == "piece" and item["ingredient_id"] in PIECE_WEIGHT_CORRECTIONS_G:
                grams = item["required_quantity"] * PIECE_WEIGHT_CORRECTIONS_G[item["ingredient_id"]]
            if grams is None and unit == "slice":
                grams = item["required_quantity"] * 30.0  # one bread slice ~ 30 g
            if grams is None:
                continue
            cat = ing_cat.get(item["ingredient_id"], "__global__")
            imputed += grams * cat_price.get(cat, cat_price["__global__"])
        rows.append({
            "recipe_id": rid,
            "calculator_cost_egp": res["net_recipe_cost_egp"],
            "priced_cost_egp": round(priced, 2),
            "piece_corrections": corrected_items,
            "imputed_cost_egp": round(imputed, 2),
            "procurement_cost_egp": res["grocery_procurement_cost_egp"],
            "price_completeness": res["price_completeness_ratio"],
            "n_unpriced": res["unpriced_ingredients_count"],
        })
    df = pd.DataFrame(rows)
    df["est_cost_egp"] = (df["priced_cost_egp"] + df["imputed_cost_egp"]).round(2)
    return df


# --------------------------------------------------------------------------- #
# Diet flags
# --------------------------------------------------------------------------- #
def _diet_flags(recipe_ingredients: pd.DataFrame, ingredients: pd.DataFrame) -> pd.DataFrame:
    tags = ingredients.set_index("ingredient_id")["dietary_tags"].fillna("").str.split(",")
    tags = tags.apply(lambda t: {x.strip() for x in t if x.strip()})
    ri = recipe_ingredients[["recipe_id", "ingredient_id"]].copy()
    ri["tags"] = ri["ingredient_id"].map(tags).apply(lambda t: t if isinstance(t, set) else set())
    ri["vegan"] = ri["tags"].apply(lambda t: "vegan" in t)
    ri["vegetarian"] = ri["tags"].apply(lambda t: bool(t & {"vegan", "vegetarian"}))
    ri["pescatarian"] = ri["tags"].apply(lambda t: bool(t & {"vegan", "vegetarian", "pescatarian"}))
    out = ri.groupby("recipe_id")[["vegan", "vegetarian", "pescatarian"]].all()
    return out.add_prefix("is_").reset_index()


# --------------------------------------------------------------------------- #
# Analysis table
# --------------------------------------------------------------------------- #
@lru_cache(maxsize=4)
def _cached_recipe_table(db_path: str) -> pd.DataFrame:
    t = load_tables(Path(db_path))
    r = t["recipes"].rename(columns={"prep_time_min": "prep_time", "cook_time_min": "cook_time"})
    df = r[["recipe_id", "recipe_name_en", "recipe_name_ar", "description", "cuisine", "category",
            "base_servings", "prep_time", "cook_time", "difficulty"]].copy()
    df["family"] = df["recipe_name_en"].map(recipe_family)
    df["is_variant"] = df["family"] != df["recipe_name_en"]
    # family_id = the base (non-variant) recipe id when it exists
    base_ids = df[~df["is_variant"]].set_index("family")["recipe_id"]
    df["family_id"] = df["family"].map(base_ids).fillna(df["recipe_id"])
    df["total_time"] = df["prep_time"] + df["cook_time"]
    df["difficulty_level"] = df["difficulty"].map(DIFFICULTY_ORDER)
    df["n_ingredients"] = df["recipe_id"].map(t["recipe_ingredients"].groupby("recipe_id").size())

    df = df.merge(_diet_flags(t["recipe_ingredients"], t["ingredients"]), on="recipe_id", how="left")
    df = df.merge(compute_recipe_costs(Path(db_path), t), on="recipe_id", how="left")
    servings = df["base_servings"].clip(lower=1)
    df["priced_cost_per_serving"] = (df["priced_cost_egp"] / servings).round(2)
    df["est_cost_per_serving"] = (df["est_cost_egp"] / servings).round(2)
    return df


def build_recipe_table(db_path: Path = DB_PATH) -> pd.DataFrame:
    """One row per recipe with features, diet flags and costs (cached)."""
    return _cached_recipe_table(str(Path(db_path).resolve())).copy()


def unique_recipes(recipe_table: pd.DataFrame) -> pd.DataFrame:
    """Keep one recipe per family (the base recipe) — removes duplicated variants."""
    return recipe_table[recipe_table["recipe_id"] == recipe_table["family_id"]].reset_index(drop=True)


def ingredient_matrix(recipe_ingredients: pd.DataFrame, recipe_ids) -> pd.DataFrame:
    """Binary recipe x ingredient matrix (rows ordered like recipe_ids)."""
    m = pd.crosstab(recipe_ingredients["recipe_id"], recipe_ingredients["ingredient_id"]).clip(upper=1)
    return m.reindex(list(recipe_ids)).fillna(0).astype(np.int8)
