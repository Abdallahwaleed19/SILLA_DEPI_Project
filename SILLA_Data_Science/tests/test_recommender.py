"""Tests for the SILLA content-based recommender and data loader."""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from SILLA_Data_Science.data_loader import build_recipe_table, recipe_family, unique_recipes  # noqa: E402
from SILLA_Data_Science.recommender import ContentBasedRecommender, Weights  # noqa: E402


@pytest.fixture(scope="module")
def rec():
    return ContentBasedRecommender().fit()


# ------------------------------------------------------------ data loader
def test_recipe_family_strips_only_style_suffixes():
    assert recipe_family("Egyptian Koshari (Cairo Street Style)") == "Egyptian Koshari"
    assert recipe_family("Chicken Tikka Masala (Murgh Makhani)") == "Chicken Tikka Masala (Murgh Makhani)"


def test_recipe_table_shape_and_costs():
    df = build_recipe_table()
    assert len(df) == 320
    assert df["recipe_id"].is_unique
    assert (df["est_cost_per_serving"] > 0).all()
    assert (df["est_cost_egp"] >= df["priced_cost_egp"]).all()
    assert len(unique_recipes(df)) == df["family_id"].nunique()


def test_piece_weight_correction_fixes_cardamom():
    df = build_recipe_table().set_index("recipe_id")
    # Molokhia with chicken uses 4 cardamom pods; the raw calculator counts 400 g
    assert df.loc["R0003", "priced_cost_egp"] < df.loc["R0003", "calculator_cost_egp"] - 500
    assert df.loc["R0003", "est_cost_per_serving"] < 100


def test_diet_flags_are_nested():
    df = build_recipe_table()
    assert (df["is_vegetarian"] | ~df["is_vegan"]).all()
    assert (df["is_pescatarian"] | ~df["is_vegetarian"]).all()


# ------------------------------------------------------------ recommender
def test_similarity_matrix_is_symmetric_and_bounded(rec):
    s = rec.similarity
    assert s.shape == (320, 320)
    assert np.allclose(s, s.T)
    assert s.min() >= -1e-9 and s.max() <= 1 + 1e-9


def test_similar_recipes_excludes_self_and_variants(rec):
    res = rec.similar_recipes("R0002", k=5)
    assert len(res) == 5
    fams = rec.recipes.set_index("recipe_id")["family_id"]
    assert fams["R0002"] not in set(fams[res["recipe_id"]])
    assert fams[res["recipe_id"]].is_unique
    assert not rec.recipes.set_index("recipe_id").loc[res["recipe_id"], "is_variant"].any()


def test_cheaper_alternatives_are_cheaper(rec):
    res = rec.alternatives("R0001", k=5, cheaper=True)
    ref = rec.recipes.set_index("recipe_id").loc["R0001", "est_cost_per_serving"]
    assert len(res) > 0
    assert (res["est_cost_per_serving"] < ref).all()


def test_diet_filter(rec):
    res = rec.alternatives("R0003", k=5, diet="vegetarian", same_category=False)
    flags = rec.recipes.set_index("recipe_id")["is_vegetarian"]
    assert len(res) > 0 and flags[res["recipe_id"]].all()


def test_exclude_ingredients_arabic_and_english(rec):
    beef = rec.resolve_ingredients(["beef"])
    assert "ING0067" in beef  # Ground Beef
    assert rec.resolve_ingredients(["الفراخ"])  # Egyptian colloquial for chicken
    res = rec.alternatives("R0001", k=5, exclude_ingredients=["beef"])
    for rid in res["recipe_id"]:
        assert not (rec.recipe_ingredient_sets[rec._pos[rid]] & beef)


def test_budget_and_time_filters(rec):
    res = rec.recommend(liked_recipe_ids=["R0001"], max_cost_per_serving=25, max_total_time=40, k=5)
    assert len(res) > 0
    assert (res["est_cost_per_serving"] <= 25).all()
    assert (res["total_time"] <= 40).all()


def test_pantry_increases_coverage(rec):
    pantry = ["rice", "onion", "tomato", "garlic", "lentils", "pasta"]
    res = rec.recommend(pantry=pantry, k=5)
    assert "pantry_coverage" in res.columns
    assert res["pantry_coverage"].mean() > 0.3


def test_explain_sums_to_total(rec):
    parts = rec.explain("R0001", "R0114")
    total = parts.pop("total")
    assert abs(sum(parts.values()) - total) < 1e-3


def test_unknown_recipe_raises(rec):
    with pytest.raises(KeyError):
        rec.similar_recipes("R9999")


def test_weights_change_ranking():
    r1 = ContentBasedRecommender(Weights(1, 0, 0, 0, 0)).fit()
    r2 = ContentBasedRecommender(Weights(0, 0, 0, 0, 1)).fit()
    assert list(r1.similar_recipes("R0002")["recipe_id"]) != list(r2.similar_recipes("R0002")["recipe_id"])


def test_arabic_meat_group_excludes_all_red_meat(rec):
    meat = rec.resolve_ingredients(["لحم"])
    assert {"ING0008", "ING0067", "ING0078"} <= meat  # sirloin, ground beef, minced lamb
    res = rec.alternatives("R0001", k=5, exclude_ingredients=["لحم"])
    assert len(res) > 0
    for rid in res["recipe_id"]:
        assert not (rec.recipe_ingredient_sets[rec._pos[rid]] & meat)
    assert rec.resolve_ingredients(["مأكولات بحرية"]) == rec.resolve_ingredients(["seafood"])
