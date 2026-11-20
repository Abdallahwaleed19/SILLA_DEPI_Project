"""
Builds and executes the three analysis notebooks in SILLA_Data_Science/notebooks/.

    python SILLA_Data_Science/build_notebooks.py

The notebooks are generated from this file so they stay reproducible; figures are
also written to SILLA_Data_Science/reports/figures/ for the evaluation report.
"""

from pathlib import Path

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

HERE = Path(__file__).resolve().parent
NB_DIR = HERE / "notebooks"

SETUP = r'''
import sys, warnings
from pathlib import Path
ROOT = next(p for p in [Path.cwd(), *Path.cwd().parents] if (p / "SILLA_Data_Engineering").exists())
sys.path.insert(0, str(ROOT))
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from SILLA_Data_Science.data_loader import FIGURES_DIR, build_recipe_table, load_tables, unique_recipes

FIGURES_DIR.mkdir(parents=True, exist_ok=True)
pd.set_option("display.width", 200); pd.set_option("display.max_columns", 30); pd.set_option("display.max_colwidth", 60)

# Chart style: one accent colour, quiet axes, light grid
ACCENT, ACCENT_2, ACCENT_3, MUTED = "#2a78d6", "#eb6834", "#1baf7a", "#52514e"
plt.rcParams.update({
    "figure.dpi": 110, "savefig.dpi": 150, "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": "#b5b4ad", "axes.grid": True, "grid.color": "#e6e5df", "grid.linewidth": 0.8,
    "axes.axisbelow": True, "axes.titleweight": "bold", "axes.titlesize": 11, "axes.labelsize": 9,
    "xtick.labelsize": 8, "ytick.labelsize": 8, "axes.labelcolor": MUTED, "xtick.color": MUTED, "ytick.color": MUTED,
})
def save(fig, name):
    fig.tight_layout(); fig.savefig(FIGURES_DIR / f"{name}.png", bbox_inches="tight")
'''


def md(s):
    return new_markdown_cell(s.strip())


def code(s):
    return new_code_cell(s.strip())


# --------------------------------------------------------------------------- #
# 01 — EDA
# --------------------------------------------------------------------------- #
EDA = [
    md("""
# SILLA — 01 · Exploratory Data Analysis
**Owner:** Amr Badr · Data Science & Recommendation
**تحليل استكشافي للوصفات والمكونات والأسعار**

Questions this notebook answers:
1. What does the recipe catalogue look like (categories, cuisines, difficulty, time)?
2. Which ingredients drive the catalogue, and how do they combine?
3. How are product prices distributed across ingredient categories and stores?
4. How much does a meal cost per serving, and what makes it expensive?
5. Which data-quality issues affect recommendation and cost modelling?

Data source: `SILLA_Data_Engineering/database/silla_staging.db` (built by the Data Engineering pipeline).
"""),
    code(SETUP),
    code('''
tables = load_tables()
recipes_all = build_recipe_table()          # 320 rows, with costs and diet flags
recipes = unique_recipes(recipes_all)       # one row per dish (see section 1)
ri, ingredients, products, stores = (tables[k] for k in ["recipe_ingredients", "ingredients", "products", "stores"])
ing_name = ingredients.set_index("ingredient_id")["canonical_name_en"]
store_name = stores.set_index("store_id")["store_name"]
pd.DataFrame({name: {"rows": len(df), "columns": df.shape[1], "missing cells": int(df.isna().sum().sum())}
              for name, df in tables.items()}).T
'''),
    md("""
## 1. Data quality
### 1.1 Recipe style variants are duplicates
Many recipe names end with a style suffix such as *(Cairo Street Style)*. These variants have
**exactly the same ingredients and quantities** as their base recipe, so they add no new information.
For recommendation they must never be suggested for each other, and for modelling they must not leak between train and test sets.
"""),
    code('''
fam_sizes = recipes_all.groupby("family_id").size()
ri_sig = ri.sort_values(["recipe_id", "ingredient_id"]).groupby("recipe_id").apply(
    lambda g: tuple(zip(g.ingredient_id, g.quantity, g.unit)))
same = recipes_all.assign(sig=recipes_all.recipe_id.map(ri_sig)).groupby("family_id")["sig"].nunique().eq(1).all()
print(f"Recipes: {len(recipes_all)} | unique dishes (families): {recipes_all.family_id.nunique()} | "
      f"style variants: {recipes_all.is_variant.sum()}")
print("Family sizes:", fam_sizes.value_counts().sort_index().to_dict())
print("Every variant has identical ingredients/quantities to its base recipe:", same)
recipes_all.loc[recipes_all.family_id == "R0002", ["recipe_id", "recipe_name_en", "total_time"]]
'''),
    md("""
### 1.2 Price coverage
Only ingredients that have a product in the catalogue can be priced. Missing prices are **imputed** with the
median price per gram of the ingredient's category (e.g. *Meat and Poultry*) so that recipes can be compared fairly.
"""),
    code('''
priced_ings = set(products.ingredient_id)
print(f"Ingredients with at least one product: {len(priced_ings)}/{len(ingredients)}")
print(f"Dishes with 100% real prices: {(recipes.price_completeness == 1).sum()}/{len(recipes)}")
print(f"Share of estimated cost that is imputed: {recipes.imputed_cost_egp.sum() / recipes.est_cost_egp.sum():.1%}")
use = ri[ri.recipe_id.isin(recipes.recipe_id)]
missing = (use[~use.ingredient_id.isin(priced_ings)].ingredient_id.value_counts().head(10)
           .rename(index=ing_name).rename("dishes using it"))
missing.to_frame()
'''),
    code('''
fig, ax = plt.subplots(figsize=(6, 3))
ax.hist(recipes.price_completeness * 100, bins=np.arange(35, 105, 5), color=ACCENT, edgecolor="white", linewidth=2)
ax.set(title="Share of each dish's ingredients with a real price", xlabel="Price completeness (%)", ylabel="Dishes")
save(fig, "eda_price_completeness")
'''),
    md("""
### 1.3 Unit-conversion issue in the shared cost calculator
`SILLA_Recommendation/cost_calculator.py` converts *piece → gram* with a 100 g default for any ingredient missing
from its produce table (whose IDs no longer match the ingredients table). Whole spices are listed in pieces, so
**4 cardamom pods become 400 g (≈ 600 EGP)**. `data_loader.py` applies realistic per-piece weights
(cardamom 0.2 g, bay leaf 0.2 g, clove 0.1 g, cinnamon stick 3 g, mastic 0.1 g, egg 60 g) on top of the calculator output.
*This should also be fixed in the shared module by its owner.*
"""),
    code('''
fix = recipes_all.assign(error=recipes_all.calculator_cost_egp - recipes_all.priced_cost_egp)
print(f"Recipes affected: {(fix.piece_corrections > 0).sum()} | largest over-estimate: {fix.error.max():,.0f} EGP")
fix.nlargest(6, "error")[["recipe_name_en", "calculator_cost_egp", "priced_cost_egp", "error"]]
'''),
    md("""
### 1.4 Other observations
- Some recipes are incomplete, e.g. *Egyptian Orzo Chicken Soup* has no chicken in its ingredient list.
- Dietary tags exist per ingredient but `gluten-free` is only set on vegan items, so a recipe-level gluten-free flag would be unreliable. Vegan / vegetarian / pescatarian flags are derived (a recipe is vegetarian when every ingredient is).
"""),
    md("## 2. Recipes (unique dishes)"),
    code('''
fig, axes = plt.subplots(1, 2, figsize=(10, 3.4))
c = recipes.category.value_counts().sort_values()
axes[0].barh(c.index, c.values, color=ACCENT, height=0.6); axes[0].set(title="Dishes by category", xlabel="Dishes")
cu = recipes.cuisine.value_counts(); cu = pd.concat([cu.head(6), pd.Series({"Other": cu.iloc[6:].sum()})]).sort_values()
axes[1].barh(cu.index, cu.values, color=ACCENT, height=0.6); axes[1].set(title="Dishes by cuisine", xlabel="Dishes")
for ax in axes: ax.grid(axis="y", visible=False)
save(fig, "eda_category_cuisine")
'''),
    code('''
fig, axes = plt.subplots(1, 3, figsize=(12, 3))
axes[0].hist(recipes.total_time, bins=15, color=ACCENT, edgecolor="white", linewidth=2)
axes[0].set(title="Total time (prep + cook)", xlabel="Minutes", ylabel="Dishes")
axes[1].hist(recipes.n_ingredients, bins=np.arange(1.5, 15.5, 1), color=ACCENT, edgecolor="white", linewidth=2)
axes[1].set(title="Ingredients per dish", xlabel="Ingredients")
d = recipes.difficulty.value_counts().reindex(["Easy", "Medium", "Hard"])
axes[2].bar(d.index, d.values, color=ACCENT, width=0.55); axes[2].set(title="Difficulty"); axes[2].grid(axis="x", visible=False)
save(fig, "eda_time_ingredients_difficulty")
recipes[["base_servings", "prep_time", "cook_time", "total_time", "n_ingredients"]].describe().round(1)
'''),
    code('''
diet = recipes[["is_vegan", "is_vegetarian", "is_pescatarian"]].mean().rename(lambda s: s[3:].title()) * 100
diet.round(1).to_frame("% of dishes")
'''),
    md("## 3. Ingredients"),
    code('''
use = ri[ri.recipe_id.isin(recipes.recipe_id)]
top = use.ingredient_id.value_counts().head(20).rename(index=ing_name).sort_values()
fig, ax = plt.subplots(figsize=(6.5, 5))
ax.barh(top.index, top.values, color=ACCENT, height=0.6); ax.grid(axis="y", visible=False)
ax.set(title="20 most used ingredients", xlabel="Number of dishes")
save(fig, "eda_top_ingredients")
'''),
    code('''
cat_use = use.merge(ingredients[["ingredient_id", "category"]]).groupby("category").recipe_id.nunique().sort_values()
fig, ax = plt.subplots(figsize=(6.5, 3.6))
ax.barh(cat_use.index, cat_use.values / len(recipes) * 100, color=ACCENT, height=0.6); ax.grid(axis="y", visible=False)
ax.set(title="Share of dishes using each ingredient category", xlabel="% of dishes")
save(fig, "eda_ingredient_categories")
'''),
    code('''
# Co-occurrence of the 15 most common non-staple ingredients
staples = {"ING0051", "ING0012", "ING0126"}  # salt, black pepper, cooking oil
top15 = [i for i in use.ingredient_id.value_counts().index if i not in staples][:15]
m = pd.crosstab(use.recipe_id, use.ingredient_id).clip(upper=1)[top15]
arr = (m.T @ m).to_numpy().copy(); np.fill_diagonal(arr, 0)
names = [ing_name[i] for i in top15]; co = pd.DataFrame(arr, index=names, columns=names)
fig, ax = plt.subplots(figsize=(7.5, 6))
sns.heatmap(co, cmap="Blues", ax=ax, cbar_kws={"label": "Dishes using both"}, linewidths=0.5, linecolor="white")
ax.set_title("Ingredient co-occurrence (top 15, staples excluded)")
save(fig, "eda_cooccurrence")
'''),
    md("## 4. Product prices"),
    code('''
p = products.merge(ingredients[["ingredient_id", "category"]].rename(columns={"category": "ing_category"}), on="ingredient_id")
p["store"] = p.store_id.map(store_name)
p = p[p.package_unit.isin(["g", "ml"])].assign(egp_per_kg=lambda d: d.price_egp / d.package_size * 1000)
order = p.groupby("ing_category").egp_per_kg.median().sort_values().index
fig, ax = plt.subplots(figsize=(8, 4))
sns.boxplot(data=p, y="ing_category", x="egp_per_kg", order=order, color=ACCENT, ax=ax, fliersize=2, linewidth=0.8,
            boxprops={"alpha": 0.85})
ax.set_xscale("log"); ax.set(title="Price per kg / litre by ingredient category (log scale)", xlabel="EGP per kg or litre", ylabel="")
save(fig, "eda_price_per_kg")
p.groupby("ing_category").egp_per_kg.describe()[["count", "min", "50%", "max"]].round(1).sort_values("50%")
'''),
    code('''
by_store = products.store_id.map(store_name).value_counts().sort_values()
multi = p.groupby("ingredient_id").filter(lambda g: g.store_id.nunique() > 1)
cheapest = multi.loc[multi.groupby("ingredient_id").egp_per_kg.idxmin(), "store"].value_counts().reindex(by_store.index).fillna(0)
fig, axes = plt.subplots(1, 2, figsize=(10, 3))
axes[0].barh(by_store.index, by_store.values, color=ACCENT, height=0.6); axes[0].set(title="Products listed per store", xlabel="Products")
axes[1].barh(cheapest.index, cheapest.values, color=ACCENT, height=0.6)
axes[1].set(title="Cheapest store for an ingredient", xlabel="Ingredients (sold in 2+ stores)")
for ax in axes: ax.grid(axis="y", visible=False)
save(fig, "eda_stores")
spread = multi.groupby("ingredient_id").egp_per_kg.agg(lambda x: x.max() / x.min())
print(f"Ingredients sold in more than one store: {multi.ingredient_id.nunique()} | "
      f"median price ratio (most / least expensive store): {spread.median():.2f}x")
'''),
    md("## 5. Meal cost per serving"),
    code('''
fig, axes = plt.subplots(1, 2, figsize=(11, 3.6))
axes[0].hist(recipes.est_cost_per_serving, bins=25, color=ACCENT, edgecolor="white", linewidth=1.5)
axes[0].axvline(recipes.est_cost_per_serving.median(), color=MUTED, ls="--", lw=1)
axes[0].text(recipes.est_cost_per_serving.median() * 1.05, axes[0].get_ylim()[1] * 0.9,
             f"median {recipes.est_cost_per_serving.median():.0f} EGP", fontsize=8, color=MUTED)
axes[0].set(title="Estimated cost per serving", xlabel="EGP per serving", ylabel="Dishes")
order = recipes.groupby("category").est_cost_per_serving.median().sort_values().index
sns.boxplot(data=recipes, y="category", x="est_cost_per_serving", order=order, color=ACCENT, ax=axes[1],
            fliersize=2, linewidth=0.8)
axes[1].set(title="Cost per serving by category", xlabel="EGP per serving", ylabel="")
save(fig, "eda_cost_per_serving")
recipes.groupby("category").est_cost_per_serving.describe()[["count", "min", "50%", "max"]].round(1).sort_values("50%")
'''),
    code('''
cols = ["recipe_name_en", "category", "est_cost_per_serving", "price_completeness"]
pd.concat({"Most expensive": recipes.nlargest(5, "est_cost_per_serving")[cols].reset_index(drop=True),
           "Cheapest": recipes.nsmallest(5, "est_cost_per_serving")[cols].reset_index(drop=True)})
'''),
    code('''
num = recipes[["est_cost_per_serving", "total_time", "n_ingredients", "difficulty_level", "base_servings"]]
mix = use.merge(ingredients[["ingredient_id", "category"]]).pivot_table(index="recipe_id", columns="category",
                                                                       values="ingredient_id", aggfunc="count", fill_value=0)
num = num.set_index(recipes.recipe_id).join(mix[["Meat and Poultry", "Seafood", "Vegetables", "Dairy and Eggs"]].add_prefix("n "))
corr = num.corr(method="spearman")[["est_cost_per_serving"]].drop("est_cost_per_serving").sort_values("est_cost_per_serving")
fig, ax = plt.subplots(figsize=(6, 3.4))
ax.barh(corr.index, corr.est_cost_per_serving, color=[ACCENT if v > 0 else ACCENT_2 for v in corr.est_cost_per_serving], height=0.6)
ax.axvline(0, color=MUTED, lw=0.8); ax.grid(axis="y", visible=False)
ax.set(title="What drives cost per serving? (Spearman correlation)", xlabel="Correlation with cost per serving")
save(fig, "eda_cost_drivers")
corr.round(2)
'''),
    md("""
## 6. Key insights
1. **320 recipes = 155 unique dishes.** 165 recipes are style variants with identical ingredients; recommendation and
   modelling must work at the dish level (family) to avoid duplicate suggestions and train/test leakage.
2. **Egyptian main courses dominate** (≈ two-thirds Egyptian, half Main Course). Small categories (Appetizer, Soup) offer few alternatives.
3. **A few staples appear everywhere** — salt, garlic, onion, black pepper, ghee. Ingredient similarity must down-weight
   them (TF-IDF), otherwise every recipe looks similar.
4. **Protein decides the price.** Seafood and meat/poultry counts are the strongest cost drivers; seafood dishes have the
   highest median cost per serving, drinks/appetizers/salads the lowest. More ingredients and longer cooking also correlate with cost.
5. **Prices are nearly identical across stores** for most ingredients (median price ratio ≈ 1.04×), with Hyperone and Lulu
   most often the cheapest — store choice matters less than recipe choice.
6. **Price coverage is incomplete:** only 6 dishes are 100% priced and about a third of total cost is imputed
   (mostly oil, milk, salt, herbs). Costs are therefore estimates.
7. **A unit-conversion bug** in the shared cost calculator over-prices 76 recipes (up to ≈ 1,400 EGP) by treating spice
   pieces as 100 g; corrected here and reported to the module owner.
"""),
]

# --------------------------------------------------------------------------- #
# 02 — Recommendation system + evaluation
# --------------------------------------------------------------------------- #
REC = [
    md("""
# SILLA — 02 · Content-Based Recommendation System & Evaluation
**Owner:** Amr Badr · Data Science & Recommendation
**نظام توصيات قائم على المحتوى + اقتراح وصفات بديلة + تقييم الجودة**

## How it works
Each recipe is described by four content blocks; similarity is a weighted sum of block similarities:

| Block | Representation | Similarity | Weight |
|---|---|---|---|
| Ingredients | TF-IDF over ingredient presence (rare ingredients weigh more than salt) | cosine | 0.55 |
| Ingredient mix | share of ingredients per category (meat, vegetables, dairy …) | cosine | 0.10 |
| Category / cuisine | dish type and cuisine | exact match | 0.20 / 0.05 |
| Practical | log cost per serving, log total time, difficulty, number of ingredients (scaled 0–1) | 1 − mean abs. difference | 0.10 |

On top of the similarity, `alternatives()` and `recommend()` apply user preferences:
**cheaper** (only cheaper dishes + savings bonus), **diet** (vegan / vegetarian / pescatarian), **excluded ingredients**
(allergies, dislikes — English or Egyptian Arabic names), **max cost per serving**, **max time**, and the **pantry**
(bonus for dishes that use what the user already has; salt, pepper, oil and water are assumed).
Style variants of the same dish are never recommended for each other, and only one recipe per dish is returned.
"""),
    code(SETUP),
    code('''
from SILLA_Data_Science.recommender import ContentBasedRecommender, Weights
tables = load_tables()
rec = ContentBasedRecommender().fit(build_recipe_table(), tables)
show = ["recipe_id", "recipe_name_en", "category", "similarity", "est_cost_per_serving", "cost_change_pct", "shared_ingredients"]
def title(rid):
    r = rec.recipes.set_index("recipe_id").loc[rid]
    print(f"Query: {rid} · {r.recipe_name_en} / {r.recipe_name_ar} · {r.category} · {r.est_cost_per_serving:.1f} EGP per serving")
'''),
    md("## 1. Similar recipes (\"more like this\")"),
    code('''
title("R0002"); rec.similar_recipes("R0002", k=5)[show]
'''),
    code('''
title("R0001"); rec.similar_recipes("R0001", k=5)[show]
'''),
    code('''
# Why are two recipes similar? Contribution of each block to the final score
pd.DataFrame({"Macaroni Béchamel vs Moussaka With Béchamel": rec.explain("R0001", "R0114"),
              "Macaroni Béchamel vs Koshari": rec.explain("R0001", "R0002")})
'''),
    md("## 2. Alternative recipes by cost, ingredients and preferences"),
    code('''
print("Cheaper alternatives:"); title("R0003")
rec.alternatives("R0003", k=5, cheaper=True)[show]
'''),
    code('''
print("Vegetarian alternatives to a meat dish:"); title("R0001")
rec.alternatives("R0001", k=5, diet="vegetarian", same_category=False)[show]
'''),
    code('''
print("Without beef (allergy / dislike), using the Arabic word لحم:"); title("R0001")
print("Excluded:", sorted(rec.ingredients.loc[list(rec.resolve_ingredients(["لحم"])), "canonical_name_en"]))
rec.alternatives("R0001", k=5, exclude_ingredients=["لحم"])[show]
'''),
    code('''
print("What can I cook with what I have, under 30 EGP per serving?")
pantry = ["رز", "بصل", "طماطم", "عدس", "مكرونة", "ثوم"]
print("Pantry resolved to:", sorted(rec.ingredients.loc[list(rec.resolve_ingredients(pantry)), "canonical_name_en"]))
rec.recommend(pantry=pantry, max_cost_per_serving=30, k=5)[
    ["recipe_name_en", "category", "pantry_coverage", "missing_ingredients", "est_cost_per_serving"]]
'''),
    code('''
print("User liked Koshari and Molokhia; vegan, under 45 minutes:")
rec.recommend(liked_recipe_ids=["R0002", "R0003"], diet="vegan", max_total_time=45, k=5)[
    ["recipe_name_en", "category", "score", "est_cost_per_serving", "total_time"]]
'''),
    md("""
## 3. Evaluation
There are no user ratings or purchases yet, so the recommender is evaluated **offline with content-based proxy metrics**.
Each of the 155 unique dishes is used once as a query, top-5 lists are scored and averaged.

| Metric | Meaning | Better |
|---|---|---|
| category_precision@5 | share of recommendations in the same dish category | ↑ |
| ingredient_jaccard@5 | ingredient overlap with the query | ↑ |
| description_sim@5 | TF-IDF similarity of the recipe **descriptions** — text the recommender never sees (independent judge) | ↑ |
| nDCG@5 (description) | ranking quality with description similarity as gain; duplicates get 0 | ↑ |
| cost_gap@5 | mean \\|log(cost ratio)\\| to the query | ↓ |
| diversity@5 | 1 − mean pairwise ingredient similarity inside the list | ↑ (balance) |
| duplicate_rate | share of suggestions that are just a style variant of the query | ↓ |
| catalog_coverage | share of dishes recommended at least once | ↑ |
"""),
    code('''
from SILLA_Data_Science.evaluation import run_all
results = run_all(save=True)
comp = results["method_comparison"]
comp.round(3)
'''),
    code('''
metrics = [("category_precision", "Category precision@5 ↑"), ("ndcg_description", "nDCG@5 (description) ↑"),
           ("cost_gap", "Cost gap@5 ↓"), ("duplicate_rate", "Duplicate rate ↓")]
labels = {"Random": "Random", "Same category (random)": "Same category", "Naive ingredient cosine (no variant filter)": "Naive cosine",
          "Ingredients only (TF-IDF)": "Ingredients TF-IDF", "Hybrid content-based (SILLA)": "SILLA hybrid"}
fig, axes = plt.subplots(1, 4, figsize=(14, 3.2), sharey=True)
for ax, (m, t) in zip(axes, metrics):
    vals = comp[m].rename(index=labels)
    ax.barh(vals.index, vals.values, color=[ACCENT if i == "SILLA hybrid" else "#b5b4ad" for i in vals.index], height=0.6)
    for y, v in enumerate(vals.values):
        ax.text(v, y, f" {v:.2f}", va="center", fontsize=8, color="#30342f")
    ax.set_title(t); ax.grid(axis="y", visible=False); ax.set_xlim(0, max(vals.max() * 1.3, 0.1))
save(fig, "rec_method_comparison")
'''),
    code('''
results["weight_sensitivity"].round(3)
'''),
    code('''
sc = results["scenarios"]
sc[["queries", "success_rate", "avg_results", "constraint_compliance", "avg_similarity", "avg_cost_change_pct",
    "pantry_coverage_with_pantry", "pantry_coverage_without_pantry"]]
'''),
    md("""
## 4. Conclusions
- **The hybrid recommender beats every baseline on ranking quality** (highest nDCG with description similarity as an
  independent judge, ≈ 3.4× random) while keeping **95% of suggestions in the same dish category** and the **closest price level** (lowest cost gap).
- **Naive ingredient cosine looks good on paper but is useless in practice:** about 21% of its suggestions are style
  variants of the query (the same dish with a different name). The family filter removes these completely (0%).
- **Ingredients alone** give high overlap but mix categories (61% same category: a dessert can be suggested for a main course);
  adding category, cost and time features fixes this with almost no loss in description similarity.
- **Preference constraints are always respected** (100% compliance for cheaper, vegetarian, excluded ingredient and budget).
  Cheaper alternatives save on average ≈ 47% per serving, and a cheaper option exists for ≈ 95% of dishes.
- **The pantry bonus raises the share of already-owned ingredients** in the suggestions; its weight can be tuned with real usage.
- **Limitations:** no user feedback yet (metrics are proxies); costs are partly imputed; small categories limit alternatives.
  Next step: log user clicks / cart additions and evaluate with Hit-Rate@K and precision on real interactions.
"""),
]

# --------------------------------------------------------------------------- #
# 03 — Cost prediction
# --------------------------------------------------------------------------- #
COST = [
    md("""
# SILLA — 03 · Meal Cost Prediction (experiment)
**Owner:** Amr Badr · Data Science & Recommendation
**تجربة نموذج لتوقع تكلفة الوجبة**

**Goal:** predict a dish's cost per serving from *what the recipe is* — ingredient list, category, cuisine, time,
difficulty — without looking up the price list. This is useful for new recipes or recipes with missing product prices.

- **Target:** estimated cost per serving (EGP) from `data_loader` (real prices + imputation).
- **Features:** binary ingredient presence, ingredient-category counts, category, cuisine, servings, time, difficulty, number of ingredients.
  *Quantities are not used on purpose — with quantities the model would simply re-learn the price list.*
- **Rows:** 155 unique dishes (style variants removed — they are exact duplicates).
- **Validation:** 5-fold cross-validation repeated 3 times; metrics on the original EGP scale.
"""),
    code(SETUP),
    code('''
from sklearn.model_selection import RepeatedKFold
from SILLA_Data_Science.cost_model import build_features, cross_validate, leakage_demo, feature_importance, oof_predictions, SEED
tables = load_tables()
recipes_all = build_recipe_table(); recipes = unique_recipes(recipes_all)
X, y = build_features(recipes, tables)
print(f"Dishes: {len(X)} | features: {X.shape[1]} | target mean {y.mean():.1f} EGP, median {y.median():.1f} EGP")
'''),
    code('''
cv = cross_validate(X, y, RepeatedKFold(n_splits=5, n_repeats=3, random_state=SEED))
cv = pd.DataFrame(cv).T
cv.round(3)
'''),
    code('''
fig, axes = plt.subplots(1, 2, figsize=(10, 2.8), sharey=True)
names = {"Baseline: category median": "Category median", "Ridge regression (log target)": "Ridge",
         "Random forest": "Random forest", "Gradient boosting": "Gradient boosting"}
for ax, (m, t) in zip(axes, [("MAE_egp", "Mean absolute error (EGP) ↓"), ("R2", "R² ↑")]):
    v = cv[m].rename(index=names)
    best = v.idxmin() if m == "MAE_egp" else v.idxmax()
    ax.barh(v.index, v.values, color=[ACCENT if i == best else "#b5b4ad" for i in v.index], height=0.6)
    for yy, val in enumerate(v.values): ax.text(val, yy, f" {val:.2f}", va="center", fontsize=8)
    ax.set_title(t); ax.grid(axis="y", visible=False); ax.set_xlim(0, v.max() * 1.25)
save(fig, "cost_model_comparison")
'''),
    md("""
## Why duplicates must be removed (leakage check)
If the 320 rows are split randomly, a style variant can sit in the training set while its identical twin is in the test
set — the model just "remembers" the answer. Grouping by dish family gives the honest estimate.
"""),
    code('''
leakage_demo(recipes_all, tables).round(3)
'''),
    code('''
fi = feature_importance(X, y, top=15).sort_values()
fig, ax = plt.subplots(figsize=(6.5, 4.5))
ax.barh(fi.index.str.replace("n_cat_", "# ").str.replace("ing_", "").str.replace("category_", "category: "),
        fi.values, color=ACCENT, height=0.6)
ax.grid(axis="y", visible=False); ax.set(title="Top 15 features (random forest importance)", xlabel="Importance")
save(fig, "cost_feature_importance")
'''),
    code('''
pred = oof_predictions(X, y, "Gradient boosting")
fig, ax = plt.subplots(figsize=(4.8, 4.5))
ax.scatter(y, pred, s=22, color=ACCENT, alpha=0.75, edgecolor="white", linewidth=0.6)
lim = [0, max(y.max(), pred.max()) * 1.05]
ax.plot(lim, lim, color=MUTED, ls="--", lw=1); ax.set(xlim=lim, ylim=lim)
ax.set(title="Predicted vs actual (out-of-fold)", xlabel="Actual EGP per serving", ylabel="Predicted EGP per serving")
save(fig, "cost_pred_vs_actual")
err = (pred - y).rename("error")
worst = recipes.set_index("recipe_id").loc[err.abs().nlargest(6).index, ["recipe_name_en", "category"]]
worst.assign(actual=y, predicted=pred.round(1))
'''),
    md("""
## Conclusions — is the data sufficient?
- **Partly.** Gradient boosting / random forest explain about **75% of the variance** (R² ≈ 0.73–0.76) with a typical error of
  ≈ 12–13 EGP per serving, clearly better than the category-median baseline (R² ≈ 0.54) and linear Ridge.
- **Protein is the signal:** the number of meat/poultry and seafood ingredients dominates the importance ranking.
- **Leakage matters:** with duplicate variants left in, the same model would report R² ≈ 0.90 — an over-optimistic number.
- **Not production-ready:** only 155 dishes, ~half of predictions are within ±25%, and the target itself is partly imputed.
  Use it as a rough estimate for *new* recipes (e.g. "≈ 40–60 EGP per serving"), while existing recipes should keep using the
  exact cost calculator. More recipes and fuller price coverage are needed before relying on it.
"""),
]


def build(name, cells):
    nb = new_notebook(cells=cells, metadata={"kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"},
                                             "language_info": {"name": "python"}})
    ExecutePreprocessor(timeout=900, kernel_name="python3").preprocess(nb, {"metadata": {"path": str(NB_DIR)}})
    nbformat.write(nb, NB_DIR / name)
    print("written", NB_DIR / name)


if __name__ == "__main__":
    NB_DIR.mkdir(exist_ok=True)
    build("01_eda.ipynb", EDA)
    build("02_recommendation_system.ipynb", REC)
    build("03_cost_prediction.ipynb", COST)
