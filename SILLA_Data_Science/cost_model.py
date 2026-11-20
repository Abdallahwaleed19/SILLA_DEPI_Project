"""
SILLA_Data_Science/cost_model.py
================================
Experiment: can we predict a meal's cost per serving from what the recipe is
(its ingredient list, category, cuisine, time, difficulty) *without* looking up
the price list? Useful for new recipes or recipes whose ingredients are missing
from the product catalogue.

Target   : estimated cost per serving (EGP), from data_loader (real prices +
           category-median imputation for ingredients without a product).
Features : binary ingredient presence, ingredient-category counts, category,
           cuisine, servings, total time, difficulty, number of ingredients.
           Quantities are deliberately NOT used — with quantities the model would
           just re-learn the price list.
Data     : one row per dish (155). Style variants are exact duplicates and would
           leak between train and test folds; `leakage_demo()` shows the effect.
Models   : category-median baseline, Ridge (log target), Random Forest,
           Gradient Boosting — 5-fold CV repeated 3 times.

Run:  python -m SILLA_Data_Science.cost_model
Owner: Amr Badr — Data Science & Recommendation.
"""

from __future__ import annotations

import json
from typing import Dict, Tuple

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, RegressorMixin, clone
from sklearn.compose import TransformedTargetRegressor
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.linear_model import RidgeCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GroupKFold, KFold, RepeatedKFold
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from SILLA_Data_Science.data_loader import (
    REPORTS_DIR, build_recipe_table, ingredient_matrix, load_tables, unique_recipes,
)

SEED = 42
TARGET = "est_cost_per_serving"


def build_features(recipes: pd.DataFrame, tables: Dict[str, pd.DataFrame]) -> Tuple[pd.DataFrame, pd.Series]:
    ing = ingredient_matrix(tables["recipe_ingredients"], recipes["recipe_id"])
    names = tables["ingredients"].set_index("ingredient_id")["canonical_name_en"]
    cats = tables["ingredients"].set_index("ingredient_id")["category"]
    mix = ing.T.groupby(cats.reindex(ing.columns).fillna("Other").values).sum().T.add_prefix("n_cat_")
    ing.columns = ["ing_" + names.get(c, c) for c in ing.columns]
    meta = pd.DataFrame({
        "base_servings": recipes["base_servings"].values,
        "total_time": recipes["total_time"].values,
        "difficulty_level": recipes["difficulty_level"].values,
        "n_ingredients": recipes["n_ingredients"].values,
    }, index=ing.index)
    onehot = pd.get_dummies(recipes.set_index("recipe_id")[["category", "cuisine"]], dtype=float)
    X = pd.concat([meta, mix, onehot.reindex(ing.index), ing], axis=1).astype(float)
    y = pd.Series(recipes[TARGET].values, index=ing.index, name=TARGET)
    return X, y


class CategoryMedian(BaseEstimator, RegressorMixin):
    """Baseline: predict the median cost of the recipe's category."""

    def fit(self, X, y):
        cols = [c for c in X.columns if c.startswith("category_")]
        self.cols_ = cols
        cat = X[cols].values.argmax(axis=1)
        self.medians_ = pd.Series(np.asarray(y)).groupby(cat).median()
        self.global_ = float(np.median(y))
        return self

    def predict(self, X):
        cat = X[self.cols_].values.argmax(axis=1)
        return np.array([self.medians_.get(c, self.global_) for c in cat])


def models() -> Dict[str, BaseEstimator]:
    log = dict(func=np.log1p, inverse_func=np.expm1)
    return {
        "Baseline: category median": CategoryMedian(),
        "Ridge regression (log target)": TransformedTargetRegressor(
            make_pipeline(StandardScaler(), RidgeCV(alphas=np.logspace(-1, 3, 20))), **log),
        "Random forest": TransformedTargetRegressor(
            RandomForestRegressor(n_estimators=400, min_samples_leaf=2, random_state=SEED, n_jobs=-1), **log),
        "Gradient boosting": TransformedTargetRegressor(
            GradientBoostingRegressor(n_estimators=300, max_depth=3, learning_rate=0.05,
                                      subsample=0.8, random_state=SEED), **log),
    }


def _metrics(y_true, y_pred) -> Dict[str, float]:
    y_true, y_pred = np.asarray(y_true), np.asarray(y_pred)
    ape = np.abs(y_pred - y_true) / np.clip(y_true, 1, None)
    return {
        "MAE_egp": mean_absolute_error(y_true, y_pred),
        "RMSE_egp": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "R2": r2_score(y_true, y_pred),
        "MedianAPE_pct": 100 * float(np.median(ape)),
        "within_25pct": float(np.mean(ape <= 0.25)),
    }


def cross_validate(X: pd.DataFrame, y: pd.Series, cv, groups=None) -> Dict[str, Dict[str, float]]:
    out = {}
    for name, model in models().items():
        folds = []
        for tr, te in cv.split(X, y, groups):
            m = clone(model).fit(X.iloc[tr], y.iloc[tr])
            folds.append(_metrics(y.iloc[te], m.predict(X.iloc[te])))
        df = pd.DataFrame(folds)
        out[name] = {**{k: round(v, 4) for k, v in df.mean().items()},
                     "R2_std": round(float(df["R2"].std()), 4)}
    return out


def leakage_demo(recipes_all: pd.DataFrame, tables) -> pd.DataFrame:
    """Random forest on all 320 rows: plain KFold (leaky) vs GroupKFold by dish family."""
    X, y = build_features(recipes_all, tables)
    groups = recipes_all["family_id"].values
    rf = models()["Random forest"]
    rows = {}
    for label, cv in (("KFold on 320 rows (variants leak)", KFold(5, shuffle=True, random_state=SEED)),
                      ("GroupKFold by dish family (correct)", GroupKFold(5))):
        folds = [_metrics(y.iloc[te], clone(rf).fit(X.iloc[tr], y.iloc[tr]).predict(X.iloc[te]))
                 for tr, te in cv.split(X, y, groups if isinstance(cv, GroupKFold) else None)]
        rows[label] = pd.DataFrame(folds).mean().round(4).to_dict()
    return pd.DataFrame(rows).T


def feature_importance(X: pd.DataFrame, y: pd.Series, top: int = 15) -> pd.Series:
    rf = RandomForestRegressor(n_estimators=400, min_samples_leaf=2, random_state=SEED, n_jobs=-1)
    rf.fit(X, np.log1p(y))
    return pd.Series(rf.feature_importances_, index=X.columns).sort_values(ascending=False).head(top)


def oof_predictions(X: pd.DataFrame, y: pd.Series, model_name: str = "Random forest") -> pd.Series:
    pred = pd.Series(index=y.index, dtype=float)
    for tr, te in KFold(5, shuffle=True, random_state=SEED).split(X):
        m = clone(models()[model_name]).fit(X.iloc[tr], y.iloc[tr])
        pred.iloc[te] = m.predict(X.iloc[te])
    return pred


def run_all(save: bool = True) -> Dict[str, object]:
    tables = load_tables()
    recipes_all = build_recipe_table()
    recipes = unique_recipes(recipes_all)
    X, y = build_features(recipes, tables)
    cv = RepeatedKFold(n_splits=5, n_repeats=3, random_state=SEED)
    results = {
        "data": {"n_dishes": int(len(X)), "n_features": int(X.shape[1]),
                 "target_mean_egp": round(float(y.mean()), 2), "target_median_egp": round(float(y.median()), 2)},
        "cv_results": pd.DataFrame(cross_validate(X, y, cv)).T,
        "leakage_demo": leakage_demo(recipes_all, tables),
        "feature_importance": feature_importance(X, y),
    }
    if save:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        payload = {
            "data": results["data"],
            "cv_results": json.loads(results["cv_results"].to_json(orient="index")),
            "leakage_demo": json.loads(results["leakage_demo"].to_json(orient="index")),
            "feature_importance": results["feature_importance"].round(4).to_dict(),
        }
        (REPORTS_DIR / "cost_model_results.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return results


if __name__ == "__main__":
    pd.set_option("display.width", 200)
    for k, v in run_all().items():
        print(f"\n=== {k} ===")
        print(v.to_string() if hasattr(v, "to_string") else v)
