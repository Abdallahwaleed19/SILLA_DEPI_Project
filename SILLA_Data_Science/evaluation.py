"""
SILLA_Data_Science/evaluation.py
================================
Offline evaluation of the content-based recommender.

SILLA has no user interaction data yet (no ratings, clicks or purchases), so the
recommender is evaluated with content-based proxy metrics and constraint
checks. Every unique dish (155 families) is used once as a query and the top-K
list is scored on:

  Relevance
    category_precision@K  share of recommendations in the same dish category
    ingredient_jaccard@K  mean ingredient overlap (Jaccard) with the query
    description_sim@K     TF-IDF cosine between recipe *descriptions* — a text
                          field the recommender never sees, used as an
                          independent judge of "is this a similar dish?"
    nDCG@K (description)  ranking quality, gains = description similarity
                          (a style variant of the query gets gain 0)
    cost_gap@K            mean |log(cost_rec / cost_query)|  (lower = closer price)
  Beyond accuracy
    diversity@K           1 - mean pairwise ingredient similarity inside a list
    catalog_coverage      share of dishes that get recommended at least once
    duplicate_rate        share of recommendations that are a style variant of
                          the query (useless suggestions)
  Constraint scenarios (alternatives)
    cheaper / vegetarian / exclude-ingredient / pantry — success rate,
    constraint compliance, savings and similarity kept.

Run:  python -m SILLA_Data_Science.evaluation
Owner: Amr Badr — Data Science & Recommendation.
"""

from __future__ import annotations

import json
from typing import Callable, Dict, List

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from SILLA_Data_Science.data_loader import REPORTS_DIR, build_recipe_table, load_tables
from SILLA_Data_Science.recommender import ContentBasedRecommender, Weights

K = 5
SEED = 42


class Evaluator:
    def __init__(self, rec: ContentBasedRecommender, k: int = K):
        self.rec = rec
        self.k = k
        r = rec.recipes
        self.queries = r.index[r["recipe_id"] == r["family_id"]].to_numpy()  # one per dish
        self.base_mask = (r["recipe_id"] == r["family_id"]).to_numpy()
        self.ing_sim = cosine_similarity(rec.ing_tfidf)
        desc = TfidfVectorizer(stop_words="english", sublinear_tf=True).fit_transform(r["description"].fillna(""))
        self.desc_sim = cosine_similarity(desc)
        self.cost = r["est_cost_per_serving"].to_numpy(dtype=float)
        self.cat = r["category"].to_numpy(dtype=object)
        self.fam = r["family_id"].to_numpy(dtype=object)
        self.sets = rec.recipe_ingredient_sets

    # ------------------------------------------------------------ helpers
    def _jaccard(self, a: int, b: int) -> float:
        sa, sb = self.sets[a], self.sets[b]
        return len(sa & sb) / max(len(sa | sb), 1)

    def _ideal_dcg(self, q: int) -> float:
        cand = self.base_mask & (self.fam != self.fam[q])
        gains = np.sort(self.desc_sim[q, cand])[::-1][: self.k]
        return float(np.sum(gains / np.log2(np.arange(2, len(gains) + 2))))

    def score_list(self, q: int, recs: List[int]) -> Dict[str, float]:
        if not recs:
            return {}
        gains = np.array([self.desc_sim[q, j] for j in recs])
        # a style variant of the query is a useless suggestion -> gain 0 in nDCG
        ndcg_gains = np.where([self.fam[j] == self.fam[q] for j in recs], 0.0, gains)
        dcg = float(np.sum(ndcg_gains / np.log2(np.arange(2, len(gains) + 2))))
        idcg = self._ideal_dcg(q)
        pairs = [(a, b) for n, a in enumerate(recs) for b in recs[n + 1:]]
        return {
            "category_precision": np.mean([self.cat[j] == self.cat[q] for j in recs]),
            "ingredient_jaccard": np.mean([self._jaccard(q, j) for j in recs]),
            "description_sim": float(gains.mean()),
            "ndcg_description": dcg / idcg if idcg > 0 else 0.0,
            "cost_gap": np.mean([abs(np.log(self.cost[j] / self.cost[q])) for j in recs]),
            "diversity": 1 - np.mean([self.ing_sim[a, b] for a, b in pairs]) if pairs else 0.0,
            "duplicate_rate": np.mean([self.fam[j] == self.fam[q] for j in recs]),
        }

    def evaluate(self, recommend: Callable[[int], List[int]]) -> Dict[str, float]:
        rows, recommended = [], set()
        for q in self.queries:
            recs = recommend(int(q))
            recommended.update(self.fam[j] for j in recs)
            rows.append(self.score_list(int(q), recs))
        out = pd.DataFrame(rows).mean().to_dict()
        out["catalog_coverage"] = len(recommended) / len(self.queries)
        return {k: round(float(v), 4) for k, v in out.items()}

    # ------------------------------------------------------- strategies
    def hybrid(self, rec: ContentBasedRecommender) -> Callable[[int], List[int]]:
        def f(q):
            idx = rec._top_k(rec.similarity[q], np.ones(len(rec.recipes), bool), self.k,
                             exclude_families=[self.fam[q]])
            return [i for i, _ in idx]
        return f

    def random_baseline(self) -> Callable[[int], List[int]]:
        rng = np.random.default_rng(SEED)
        def f(q):
            cand = np.where(self.base_mask & (self.fam != self.fam[q]))[0]
            return list(rng.choice(cand, self.k, replace=False))
        return f

    def same_category_baseline(self) -> Callable[[int], List[int]]:
        rng = np.random.default_rng(SEED)
        def f(q):
            cand = np.where(self.base_mask & (self.fam != self.fam[q]) & (self.cat == self.cat[q]))[0]
            if len(cand) < self.k:
                extra = np.where(self.base_mask & (self.fam != self.fam[q]) & (self.cat != self.cat[q]))[0]
                cand = np.concatenate([cand, rng.choice(extra, self.k - len(cand), replace=False)])
            return list(rng.choice(cand, self.k, replace=False))
        return f

    def naive_cosine(self) -> Callable[[int], List[int]]:
        """Plain ingredient cosine that only removes the query itself."""
        def f(q):
            order = np.argsort(-self.ing_sim[q], kind="stable")
            return [int(j) for j in order if j != q][: self.k]
        return f


# ----------------------------------------------------------------- runs
def compare_methods(ev: Evaluator, rec: ContentBasedRecommender) -> pd.DataFrame:
    ing_only = ContentBasedRecommender(Weights(1, 0, 0, 0, 0)).fit(rec.recipes)
    results = {
        "Random": ev.evaluate(ev.random_baseline()),
        "Same category (random)": ev.evaluate(ev.same_category_baseline()),
        "Naive ingredient cosine (no variant filter)": ev.evaluate(ev.naive_cosine()),
        "Ingredients only (TF-IDF)": ev.evaluate(ev.hybrid(ing_only)),
        "Hybrid content-based (SILLA)": ev.evaluate(ev.hybrid(rec)),
    }
    return pd.DataFrame(results).T


def weight_sensitivity(ev: Evaluator, recipes: pd.DataFrame) -> pd.DataFrame:
    configs = {
        "ingredients 1.0": Weights(1, 0, 0, 0, 0),
        "ingredients .7 / category .3": Weights(0.7, 0, 0.3, 0, 0),
        "default (.55/.10/.20/.05/.10)": Weights(),
        "ingredients .4 / category .3 / numeric .3": Weights(0.4, 0, 0.3, 0, 0.3),
        "equal weights": Weights(0.2, 0.2, 0.2, 0.2, 0.2),
    }
    rec = ContentBasedRecommender().fit(recipes)
    rows = {}
    for name, w in configs.items():
        rec.set_weights(w)
        rows[name] = ev.evaluate(ev.hybrid(rec))
    return pd.DataFrame(rows).T


def scenario_eval(ev: Evaluator, rec: ContentBasedRecommender) -> pd.DataFrame:
    """Evaluate alternatives() under realistic user constraints."""
    r = rec.recipes
    rng = np.random.default_rng(SEED)
    doc_freq = rec.ing_matrix.iloc[ev.queries].sum()
    common = r.iloc[ev.queries]  # base dishes
    pantry_pool = (rec.ing_matrix.iloc[ev.queries].sum().sort_values(ascending=False).index[:30]).tolist()

    out = {}
    def run(name, queries, kwargs_fn, check_fn):
        n_ok, n_rec, comply, sims, extra = 0, 0, [], [], []
        for q in queries:
            rid = r.at[q, "recipe_id"]
            kw = kwargs_fn(q)
            res = rec.alternatives(rid, k=ev.k, **kw)
            if len(res):
                n_ok += 1
            n_rec += len(res)
            for _, row in res.iterrows():
                j = rec._pos[row["recipe_id"]]
                comply.append(check_fn(q, j, kw))
                sims.append(rec.similarity[q, j])
                if "cost_change_pct" in row:
                    extra.append(row["cost_change_pct"])
        out[name] = {
            "queries": len(queries),
            "success_rate": round(n_ok / max(len(queries), 1), 4),
            "avg_results": round(n_rec / max(len(queries), 1), 2),
            "constraint_compliance": round(float(np.mean(comply)), 4) if comply else None,
            "avg_similarity": round(float(np.mean(sims)), 4) if sims else None,
            "avg_cost_change_pct": round(float(np.mean(extra)), 2) if extra else None,
        }

    q_all = list(ev.queries)
    run("Unconstrained (same category)", q_all, lambda q: {}, lambda q, j, kw: True)
    run("Cheaper alternative", q_all, lambda q: {"cheaper": True},
        lambda q, j, kw: ev.cost[j] < ev.cost[q])
    non_veg = [q for q in q_all if not r.at[q, "is_vegetarian"]]
    run("Vegetarian version of a non-vegetarian dish", non_veg,
        lambda q: {"diet": "vegetarian", "same_category": False},
        lambda q, j, kw: bool(r.at[j, "is_vegetarian"]))
    def excl(q):
        # the most distinctive ingredient = the one used by the fewest dishes
        key = min(rec.recipe_ingredient_sets[q], key=lambda i: (doc_freq.get(i, 0), i))
        return {"exclude_ingredients": [key]}
    run("Exclude the key ingredient (allergy / dislike)", q_all, excl,
        lambda q, j, kw: not (rec.recipe_ingredient_sets[j] & set(kw["exclude_ingredients"])))
    run("Budget: max 30 EGP per serving", q_all, lambda q: {"max_cost_per_serving": 30},
        lambda q, j, kw: ev.cost[j] <= 30)

    # pantry: does the pantry signal surface recipes that use what the user has?
    cov_with, cov_without = [], []
    for q in q_all:
        pantry = list(rng.choice(pantry_pool, 8, replace=False))
        pid = rec._pantry_ids(pantry, True)
        rid = r.at[q, "recipe_id"]
        for res, bucket in ((rec.alternatives(rid, k=ev.k, pantry=pantry), cov_with),
                            (rec.alternatives(rid, k=ev.k), cov_without)):
            bucket += [len(rec.recipe_ingredient_sets[rec._pos[x]] & pid) / len(rec.recipe_ingredient_sets[rec._pos[x]])
                       for x in res["recipe_id"]]
    out["Pantry-aware (8 random pantry items)"] = {
        "queries": len(q_all), "success_rate": 1.0, "avg_results": ev.k,
        "constraint_compliance": None, "avg_similarity": None, "avg_cost_change_pct": None,
        "pantry_coverage_with_pantry": round(float(np.mean(cov_with)), 4),
        "pantry_coverage_without_pantry": round(float(np.mean(cov_without)), 4),
    }
    return pd.DataFrame(out).T


def run_all(save: bool = True) -> Dict[str, pd.DataFrame]:
    recipes = build_recipe_table()
    rec = ContentBasedRecommender().fit(recipes, load_tables())
    ev = Evaluator(rec)
    results = {
        "method_comparison": compare_methods(ev, rec),
        "weight_sensitivity": weight_sensitivity(ev, recipes),
        "scenarios": scenario_eval(ev, rec),
    }
    if save:
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        payload = {k: json.loads(v.to_json(orient="index")) for k, v in results.items()}
        payload["setup"] = {"k": K, "queries": int(len(ev.queries)), "weights": rec.weights.as_dict()}
        (REPORTS_DIR / "evaluation_results.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return results


if __name__ == "__main__":
    pd.set_option("display.width", 200)
    for name, df in run_all().items():
        print(f"\n=== {name} ===")
        print(df.to_string())
