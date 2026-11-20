"""
SILLA_Data_Science/recommender.py
=================================
Content-Based Recommendation System for SILLA.

Every recipe is described by four content blocks:

  1. Ingredients      — TF-IDF over ingredient presence (rare ingredients such as
                        "molokhia" weigh more than salt or oil).
  2. Ingredient mix   — share of the recipe's ingredients in each ingredient
                        category (meat, vegetables, dairy, ...).
  3. Category/cuisine — same dish type (main course, dessert, ...) and cuisine.
  4. Practical        — estimated cost per serving, total time, difficulty,
                        number of ingredients.

Similarity between two recipes is a weighted sum of the block similarities:

  sim = w_ing*cos(ing) + w_mix*cos(mix) + w_cat*[same category]
        + w_cuisine*[same cuisine] + w_num*(1 - mean |numeric diff|)

On top of the similarity the recommender supports:
  - similar recipes ("more like this")
  - alternative recipes that are cheaper / fit a diet / avoid ingredients /
    fit a budget or time limit / use what is already in the pantry
  - preference-based recommendations from several liked recipes

Style variants of the same dish (e.g. "Koshari" and "Koshari (Cairo Street
Style)") have identical ingredients, so they are never recommended for each
other and only one recipe per family is returned.

Owner: Amr Badr — Data Science & Recommendation.
"""

from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import MinMaxScaler

from SILLA_Data_Science.data_loader import DB_PATH, build_recipe_table, ingredient_matrix, load_tables

NUMERIC_FEATURES = ["log_cost", "log_time", "difficulty_level", "n_ingredients"]
DIETS = ("vegan", "vegetarian", "pescatarian")


@dataclass
class Weights:
    ingredients: float = 0.55
    ingredient_mix: float = 0.10
    category: float = 0.20
    cuisine: float = 0.05
    numeric: float = 0.10

    def as_dict(self) -> Dict[str, float]:
        return dict(self.__dict__)


PANTRY_STAPLES = ("Fine Salt", "Black Pepper", "Vegetable Cooking Oil", "Water")

# Broad words that stand for a group of ingredients ("category:" = ingredient category).
# Keys are written already normalised (see _normalize_text).
_RED_MEAT = ["beef", "lamb", "oxtail", "pastirma", "sausage"]
INGREDIENT_GROUPS = {
    "meat": _RED_MEAT, "red meat": _RED_MEAT, "لحم": _RED_MEAT, "لحوم": _RED_MEAT, "لحمه": _RED_MEAT,
    "beef": ["beef", "oxtail", "pastirma"], "بقري": ["beef", "oxtail", "pastirma"],
    "chicken": ["chicken"], "دجاج": ["chicken"], "poultry": ["chicken", "pigeon"], "طيور": ["chicken", "pigeon"],
    "fish": ["category:Seafood"], "seafood": ["category:Seafood"], "سمك": ["category:Seafood"],
    "اسماك": ["category:Seafood"], "ماكولات بحريه": ["category:Seafood"],
}

# Egyptian colloquial -> catalogue words (applied after normalisation)
COLLOQUIAL_SYNONYMS = {"فراخ": "دجاج", "رز": "ارز", "قوطه": "طماطم", "لحمه": "لحم"}


def _normalize_text(s: str) -> str:
    s = unicodedata.normalize("NFKC", str(s).lower())
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    s = re.sub("[إأآا]", "ا", s)
    s = s.replace("ة", "ه").replace("ى", "ي").replace("ـ", "")
    # drop the Arabic definite article: "الفراخ" -> "فراخ"
    s = " ".join(w[2:] if w.startswith("ال") and len(w) > 3 else w for w in s.split())
    return re.sub(r"\s+", " ", s).strip()


class ContentBasedRecommender:
    """Content-based recipe recommender (fit once, query many times)."""

    def __init__(self, weights: Optional[Weights] = None):
        self.weights = weights or Weights()
        self.recipes: Optional[pd.DataFrame] = None

    # ------------------------------------------------------------------ fit
    def fit(self, recipes: Optional[pd.DataFrame] = None,
            tables: Optional[Dict[str, pd.DataFrame]] = None) -> "ContentBasedRecommender":
        tables = tables or load_tables(DB_PATH)
        recipes = build_recipe_table() if recipes is None else recipes
        self.recipes = recipes.reset_index(drop=True).copy()
        self.ingredients = tables["ingredients"].set_index("ingredient_id")
        self._ri = tables["recipe_ingredients"]
        ids = self.recipes["recipe_id"].tolist()
        self._pos = {rid: i for i, rid in enumerate(ids)}

        # 1. ingredient TF-IDF
        self.ing_matrix = ingredient_matrix(self._ri, ids)
        self.ing_tfidf = TfidfTransformer(sublinear_tf=True).fit_transform(self.ing_matrix.values)
        self.recipe_ingredient_sets = [set(self.ing_matrix.columns[row > 0]) for row in self.ing_matrix.values]

        # 2. ingredient-category mix
        cat_of = self.ingredients["category"].reindex(self.ing_matrix.columns).fillna("Other")
        mix = self.ing_matrix.T.groupby(cat_of.values).sum().T
        self.mix = mix.div(mix.sum(axis=1).replace(0, 1), axis=0)

        # 4. numeric block (scaled to 0..1)
        num = pd.DataFrame({
            "log_cost": np.log1p(self.recipes["est_cost_per_serving"].fillna(0)),
            "log_time": np.log1p(self.recipes["total_time"].fillna(0)),
            "difficulty_level": self.recipes["difficulty_level"].fillna(0),
            "n_ingredients": self.recipes["n_ingredients"].fillna(0),
        })
        self.numeric = MinMaxScaler().fit_transform(num[NUMERIC_FEATURES])

        self._build_similarity()
        return self

    def block_similarities(self) -> Dict[str, np.ndarray]:
        cat = self.recipes["category"].to_numpy(dtype=object)
        cui = self.recipes["cuisine"].to_numpy(dtype=object)
        diff = np.abs(self.numeric[:, None, :] - self.numeric[None, :, :]).mean(axis=2)
        return {
            "ingredients": cosine_similarity(self.ing_tfidf),
            "ingredient_mix": cosine_similarity(self.mix.values),
            "category": (cat[:, None] == cat[None, :]).astype(float),
            "cuisine": (cui[:, None] == cui[None, :]).astype(float),
            "numeric": 1.0 - diff,
        }

    def _build_similarity(self) -> None:
        self._blocks = self.block_similarities()
        w = self.weights.as_dict()
        total = sum(w.values())
        self.similarity = sum(w[k] * self._blocks[k] for k in w) / total

    def set_weights(self, weights: Weights) -> "ContentBasedRecommender":
        self.weights = weights
        self._build_similarity()
        return self

    # ------------------------------------------------------------ helpers
    def resolve_ingredients(self, names: Optional[Iterable[str]]) -> set:
        """Map ingredient names (English/Arabic/aliases) or IDs to ingredient IDs."""
        if not names:
            return set()
        ing = self.ingredients
        lookup: Dict[str, str] = {}
        for iid, row in ing.iterrows():
            lookup[_normalize_text(iid)] = iid
            for col in ("canonical_name_en", "canonical_name_ar", "aliases_en", "aliases_ar"):
                for alias in str(row.get(col, "") or "").split(","):
                    if alias.strip():
                        lookup.setdefault(_normalize_text(alias), iid)
        found = set()
        for name in names:
            key = _normalize_text(name)
            key = " ".join(COLLOQUIAL_SYNONYMS.get(w, w) for w in key.split())
            if key in INGREDIENT_GROUPS:
                for term in INGREDIENT_GROUPS[key]:
                    if term.startswith("category:"):
                        found.update(ing.index[ing["category"] == term.split(":", 1)[1]])
                    else:
                        found.update(v for k, v in lookup.items() if term in k.split())
                continue
            if key in lookup:
                found.add(lookup[key])
                continue
            # whole-word match: "chicken" -> "Whole Chicken", "Chicken Breast", ...
            words = set(key.split())
            found.update(v for k, v in lookup.items() if words and words <= set(k.split()))
        return found

    def staple_ids(self) -> set:
        """Basics assumed to be in every kitchen (salt, pepper, oil, water)."""
        return self.resolve_ingredients(PANTRY_STAPLES)

    def _pantry_ids(self, pantry, assume_staples: bool) -> set:
        ids = self.resolve_ingredients(pantry)
        if ids and assume_staples:
            ids |= self.staple_ids()
        return ids

    def _row(self, recipe_id: str) -> int:
        if recipe_id not in self._pos:
            raise KeyError(f"Unknown recipe_id: {recipe_id}")
        return self._pos[recipe_id]

    def _filter_mask(self, diet=None, exclude_ids=frozenset(), max_cost=None, max_time=None,
                     categories=None, cuisines=None) -> np.ndarray:
        r = self.recipes
        mask = np.ones(len(r), dtype=bool)
        if diet:
            if diet not in DIETS:
                raise ValueError(f"diet must be one of {DIETS}")
            mask &= r[f"is_{diet}"].fillna(False).to_numpy(dtype=bool)
        if exclude_ids:
            mask &= np.array([not (s & exclude_ids) for s in self.recipe_ingredient_sets])
        if max_cost is not None:
            mask &= (r["est_cost_per_serving"] <= max_cost).values
        if max_time is not None:
            mask &= (r["total_time"] <= max_time).values
        if categories:
            mask &= r["category"].isin(list(categories)).values
        if cuisines:
            mask &= r["cuisine"].isin(list(cuisines)).values
        return mask

    def _pantry_coverage(self, pantry_ids: set) -> np.ndarray:
        if not pantry_ids:
            return np.zeros(len(self.recipes))
        return np.array([len(s & pantry_ids) / max(len(s), 1) for s in self.recipe_ingredient_sets])

    def _format(self, picked: Sequence[tuple], ref: Optional[int] = None,
                pantry_ids: set = frozenset()) -> pd.DataFrame:
        r = self.recipes
        out = []
        for i, score in picked:
            row = {
                "recipe_id": r.at[i, "recipe_id"],
                "recipe_name_en": r.at[i, "recipe_name_en"],
                "recipe_name_ar": r.at[i, "recipe_name_ar"],
                "category": r.at[i, "category"],
                "cuisine": r.at[i, "cuisine"],
                "score": round(score, 4),
                "est_cost_per_serving": r.at[i, "est_cost_per_serving"],
                "total_time": int(r.at[i, "total_time"]),
            }
            if ref is not None:
                shared = self.recipe_ingredient_sets[i] & self.recipe_ingredient_sets[ref]
                row["similarity"] = round(float(self.similarity[ref, i]), 4)
                row["shared_ingredients"] = ", ".join(
                    sorted(self.ingredients.loc[list(shared), "canonical_name_en"]))
                ref_cost = r.at[ref, "est_cost_per_serving"]
                row["cost_change_pct"] = round(100 * (row["est_cost_per_serving"] - ref_cost) / ref_cost, 1) if ref_cost else None
            if pantry_ids:
                s = self.recipe_ingredient_sets[i]
                row["pantry_coverage"] = round(len(s & pantry_ids) / max(len(s), 1), 3)
                missing = s - pantry_ids
                row["missing_ingredients"] = ", ".join(sorted(self.ingredients.loc[list(missing), "canonical_name_en"]))
            out.append(row)
        return pd.DataFrame(out)

    def _top_k(self, scores: np.ndarray, mask: np.ndarray, k: int, exclude_families=()) -> List[tuple]:
        """
        Best k rows with at most one recipe per family. A family is ranked by its
        best-scoring member, but the base recipe is shown when it passes the
        filters (style variants share the same ingredients).
        """
        fam = self.recipes["family_id"].to_numpy(dtype=object)
        order = np.argsort(-scores, kind="stable")
        seen = set(exclude_families)
        picked = []
        for i in order:
            if not mask[i] or fam[i] in seen:
                continue
            seen.add(fam[i])
            base = self._pos.get(fam[i], i)
            picked.append((int(base if mask[base] else i), float(scores[i])))
            if len(picked) == k:
                break
        return picked

    # ------------------------------------------------------------- public
    def similar_recipes(self, recipe_id: str, k: int = 5, same_category: bool = False) -> pd.DataFrame:
        """'More like this' — the k most similar recipes (other dishes only)."""
        i = self._row(recipe_id)
        cats = [self.recipes.at[i, "category"]] if same_category else None
        mask = self._filter_mask(categories=cats)
        scores = self.similarity[i]
        idx = self._top_k(scores, mask, k, exclude_families=[self.recipes.at[i, "family_id"]])
        return self._format(idx, ref=i)

    def alternatives(self, recipe_id: str, k: int = 5, cheaper: bool = False,
                     diet: Optional[str] = None, exclude_ingredients: Optional[Iterable[str]] = None,
                     max_cost_per_serving: Optional[float] = None, max_total_time: Optional[float] = None,
                     pantry: Optional[Iterable[str]] = None, same_category: bool = True,
                     savings_weight: float = 0.3, pantry_weight: float = 0.3,
                     assume_staples: bool = True) -> pd.DataFrame:
        """
        Alternative recipes to `recipe_id` based on ingredients, cost and preferences.

        cheaper=True keeps only recipes cheaper per serving than the original and
        rewards bigger savings; `pantry` rewards recipes that use what the user has.
        """
        i = self._row(recipe_id)
        cats = [self.recipes.at[i, "category"]] if same_category else None
        exclude_ids = frozenset(self.resolve_ingredients(exclude_ingredients))
        pantry_ids = self._pantry_ids(pantry, assume_staples)
        mask = self._filter_mask(diet, exclude_ids, max_cost_per_serving, max_total_time, cats)

        scores = self.similarity[i].copy()
        if cheaper:
            ref_cost = self.recipes.at[i, "est_cost_per_serving"]
            cost = self.recipes["est_cost_per_serving"].values
            mask &= cost < ref_cost
            savings = np.clip((ref_cost - cost) / ref_cost, 0, 1) if ref_cost else np.zeros_like(cost)
            scores = scores + savings_weight * savings
        if pantry_ids:
            scores = scores + pantry_weight * self._pantry_coverage(pantry_ids)

        idx = self._top_k(scores, mask, k, exclude_families=[self.recipes.at[i, "family_id"]])
        return self._format(idx, ref=i, pantry_ids=pantry_ids)

    def recommend(self, liked_recipe_ids: Optional[Sequence[str]] = None, k: int = 5,
                  diet: Optional[str] = None, exclude_ingredients: Optional[Iterable[str]] = None,
                  max_cost_per_serving: Optional[float] = None, max_total_time: Optional[float] = None,
                  pantry: Optional[Iterable[str]] = None, categories: Optional[Iterable[str]] = None,
                  cuisines: Optional[Iterable[str]] = None, pantry_weight: float = 0.5,
                  assume_staples: bool = True) -> pd.DataFrame:
        """
        Preference-based recommendations: average similarity to the liked recipes
        (user profile) + pantry coverage, after applying hard filters.
        """
        liked = list(liked_recipe_ids or [])
        exclude_ids = frozenset(self.resolve_ingredients(exclude_ingredients))
        pantry_ids = self._pantry_ids(pantry, assume_staples)
        mask = self._filter_mask(diet, exclude_ids, max_cost_per_serving, max_total_time, categories, cuisines)

        if liked:
            rows = [self._row(r) for r in liked]
            scores = self.similarity[rows].mean(axis=0)
            excluded = {self.recipes.at[j, "family_id"] for j in rows}
        else:
            scores = np.zeros(len(self.recipes))
            excluded = set()
        if pantry_ids:
            scores = scores + pantry_weight * self._pantry_coverage(pantry_ids)
        if not liked and not pantry_ids:
            # no signal: cheapest first, as a sensible default
            c = self.recipes["est_cost_per_serving"].values
            scores = 1 - (c - c.min()) / (c.max() - c.min() + 1e-9)
        idx = self._top_k(scores, mask, k, exclude_families=excluded)
        return self._format(idx, pantry_ids=pantry_ids)

    def explain(self, recipe_a: str, recipe_b: str) -> Dict[str, float]:
        """Contribution of each content block to sim(a, b)."""
        i, j = self._row(recipe_a), self._row(recipe_b)
        w = self.weights.as_dict()
        total = sum(w.values())
        parts = {k: round(w[k] * self._blocks[k][i, j] / total, 4) for k in w}
        parts["total"] = round(float(self.similarity[i, j]), 4)
        return parts


_DEFAULT: Optional[ContentBasedRecommender] = None


def get_recommender() -> ContentBasedRecommender:
    """Shared, lazily-fitted recommender instance (for the app / other modules)."""
    global _DEFAULT
    if _DEFAULT is None:
        _DEFAULT = ContentBasedRecommender().fit()
    return _DEFAULT
