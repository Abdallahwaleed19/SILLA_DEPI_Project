# SILLA_Data_Science — EDA, Content-Based Recommendation & Cost Prediction

**Owner:** Amr Badr — Data Science & Recommendation (عمرو بدر)

| Task (from the team task sheet) | Where |
|---|---|
| EDA — recipes, prices, ingredients | [notebooks/01_eda.ipynb](notebooks/01_eda.ipynb) |
| Content-Based Recommendation System | [recommender.py](recommender.py) · [notebooks/02_recommendation_system.ipynb](notebooks/02_recommendation_system.ipynb) |
| Alternative recipes by ingredients, cost & preferences | `ContentBasedRecommender.alternatives()` / `.recommend()` |
| Evaluate recommendation quality | [evaluation.py](evaluation.py) · [reports/evaluation_report.md](reports/evaluation_report.md) |
| Meal cost prediction experiment | [cost_model.py](cost_model.py) · [notebooks/03_cost_prediction.ipynb](notebooks/03_cost_prediction.ipynb) |

## Structure
```
SILLA_Data_Science/
├── data_loader.py         # loads silla_staging.db → one row per recipe (family, diet flags, costs)
├── recommender.py         # ContentBasedRecommender
├── evaluation.py          # offline evaluation (baselines, metrics, constraint scenarios)
├── cost_model.py          # cost-per-serving prediction experiment
├── build_notebooks.py     # regenerates + executes the notebooks
├── notebooks/             # 01_eda · 02_recommendation_system · 03_cost_prediction (with outputs)
├── reports/               # evaluation_report.md, *.json results, figures/
└── tests/                 # pytest
```

## Setup
```bash
pip install -r SILLA_Data_Science/requirements.txt
```
Reads `SILLA_Data_Engineering/database/silla_staging.db` (no write). Re-uses the cost logic of
`SILLA_Recommendation/cost_calculator.py` without importing the NLP stack, so `fastembed` is **not** required.

## Usage
Run from the project root:
```python
from SILLA_Data_Science.recommender import get_recommender

rec = get_recommender()                                   # fitted once, cached

rec.similar_recipes("R0002", k=5)                         # more like Koshari
rec.alternatives("R0001", cheaper=True)                   # cheaper than Macaroni Béchamel
rec.alternatives("R0001", diet="vegetarian", same_category=False)
rec.alternatives("R0001", exclude_ingredients=["لحم"])     # no meat (Arabic or English)
rec.recommend(pantry=["رز", "بصل", "طماطم", "عدس"], max_cost_per_serving=30)
rec.recommend(liked_recipe_ids=["R0002", "R0003"], diet="vegan", max_total_time=45)
rec.explain("R0001", "R0114")                             # why are they similar?
```
Every call returns a `pandas.DataFrame` with `recipe_id`, names (EN/AR), category, score, estimated cost per serving,
time and — depending on the call — `similarity`, `cost_change_pct`, `shared_ingredients`, `pantry_coverage`, `missing_ingredients`.

Diets: `vegan`, `vegetarian`, `pescatarian`. Ingredient names accept English, Arabic, Egyptian words
(فراخ، رز، قوطة، لحمة) and groups (meat/لحم, fish/سمك, chicken/فراخ).

## Reproduce results
```bash
python -m SILLA_Data_Science.evaluation      # → reports/evaluation_results.json
python -m SILLA_Data_Science.cost_model      # → reports/cost_model_results.json
python SILLA_Data_Science/build_notebooks.py # re-executes notebooks, refreshes reports/figures
python -m pytest SILLA_Data_Science/tests
```

## Headline results
- Recommender: **95%** same-category precision, nDCG@5 **0.65** (random 0.19), **0%** duplicate suggestions, **100%** constraint compliance; cheaper alternatives save **47%** per serving on average.
- Cost model: gradient boosting **R² 0.76**, MAE **12.6 EGP**/serving vs. baseline R² 0.54 — useful as a rough estimate, not a replacement for the cost calculator.
- Data issues found: 165 duplicate style variants, 42 unpriced ingredients, a piece→gram bug in the shared cost calculator (76 recipes over-priced). Details in the [report](reports/evaluation_report.md).
