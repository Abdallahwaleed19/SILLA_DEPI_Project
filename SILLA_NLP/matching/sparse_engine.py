"""
SILLA_NLP/matching/sparse_engine.py
==================================
TF-IDF Sparse Lexical Retrieval Engine with weighted multi-field representation.
"""

import re
import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from SILLA_NLP.config.settings import STAGING_DB_PATH
from SILLA_NLP.preprocessing.query_preprocessor import normalize_arabic, strip_accents, clean_query_text


class SparseEngine:
    def __init__(self, db_path: Path = STAGING_DB_PATH):
        self.db_path = db_path
        self.recipes = {}
        self.recipe_ids = []
        self.corpus_docs = []
        self.vectorizer = None
        self.tfidf_matrix = None
        self._load_and_index()

    def _load_and_index(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT recipe_id, recipe_name_en, recipe_name_ar, description, description_ar, cuisine, category
                FROM recipes
                ORDER BY recipe_id;
            """)
            raw_recipes = cursor.fetchall()

            cursor.execute("""
                SELECT ri.recipe_id, ri.original_ingredient_name, i.canonical_name_en, i.canonical_name_ar
                FROM recipe_ingredients ri
                LEFT JOIN ingredients i ON ri.ingredient_id = i.ingredient_id;
            """)
            raw_ri = cursor.fetchall()

        ri_map = {}
        for row in raw_ri:
            rid, orig, c_en, c_ar = row[0], row[1] or "", row[2] or "", row[3] or ""
            if rid not in ri_map:
                ri_map[rid] = {"en": [], "ar": []}
            if orig: ri_map[rid]["en"].append(orig)
            if c_en and c_en != orig: ri_map[rid]["en"].append(c_en)
            if c_ar: ri_map[rid]["ar"].append(c_ar)

        for r in raw_recipes:
            rid = r[0]
            name_en = r[1] or ""
            name_ar = r[2] or ""
            desc_en = r[3] or ""
            desc_ar = r[4] or ""
            cuisine = r[5] or ""
            category = r[6] or ""
            ings = ri_map.get(rid, {"en": [], "ar": []})

            self.recipes[rid] = {
                "recipe_id": rid,
                "name_en": name_en,
                "name_ar": name_ar,
                "desc_en": desc_en,
                "desc_ar": desc_ar,
                "cuisine": cuisine,
                "category": category,
                "ingredients_en": list(set(ings["en"])),
                "ingredients_ar": list(set(ings["ar"])),
                "is_core": (1 <= int(rid.replace("R", "")) <= 16)
            }
            self.recipe_ids.append(rid)

            # Field Weighting: Title (x3), Ingredients (x2), Description (x1)
            norm_name_ar = normalize_arabic(name_ar)
            clean_name_ar = clean_query_text(name_ar)
            norm_desc_ar = normalize_arabic(desc_ar)
            norm_ings_ar = " ".join(normalize_arabic(x) for x in ings["ar"])
            clean_name_en = strip_accents(name_en)
            clean_desc_en = strip_accents(desc_en)
            ings_en = " ".join(strip_accents(x) for x in ings["en"])

            doc_text = (
                f"{norm_name_ar} {clean_name_ar} {norm_name_ar} "
                f"{clean_name_en} {clean_name_en} {clean_name_en} "
                f"{norm_ings_ar} {norm_ings_ar} {ings_en} {ings_en} "
                f"{norm_desc_ar} {clean_desc_en} {cuisine} {category}"
            )
            clean_doc = " ".join(doc_text.split()).strip()
            self.corpus_docs.append(clean_doc)

        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),
            sublinear_tf=True,
            min_df=1
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(self.corpus_docs)

    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Compute sparse TF-IDF cosine similarity scores."""
        clean_q = strip_accents(normalize_arabic(query))
        q_vec = self.vectorizer.transform([clean_q])
        sims = cosine_similarity(q_vec, self.tfidf_matrix)[0]

        top_indices = np.argsort(sims)[::-1][:top_k]
        results = [(self.recipe_ids[i], float(sims[i])) for i in top_indices]
        return results
