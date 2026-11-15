"""
SILLA_NLP/matching/dense_engine.py
==================================
Dense Semantic Retrieval Engine powered by Sentence Transformers via FastEmbed (ONNX Runtime).

Features:
- Encodes recipes into 384-dimensional dense vectors using paraphrase-multilingual-MiniLM-L12-v2.
- Pre-computes and normalizes recipe corpus embeddings.
- In-memory cosine similarity computation via fast vector dot products.
- Caches corpus embeddings to avoid redundant re-computation.
"""

import os
import sqlite3
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from fastembed import TextEmbedding

from SILLA_NLP.config.settings import (
    STAGING_DB_PATH,
    ST_MODEL_NAME,
    EMBEDDING_DIM
)


class DenseEngine:
    """
    Dense Semantic Search Engine for SILLA recipe discovery.
    """

    def __init__(
        self,
        db_path: Path = STAGING_DB_PATH,
        model_name: str = ST_MODEL_NAME,
        cache_dir: Optional[Path] = None
    ):
        self.db_path = Path(db_path)
        self.model_name = model_name
        self.cache_dir = cache_dir or (self.db_path.parent.parent / "data" / "processed")
        self.cache_file = self.cache_dir / "dense_recipe_embeddings.npy"
        
        self.recipes: Dict[str, Dict] = {}
        self.recipe_ids: List[str] = []
        self.corpus_docs: List[str] = []
        self.embeddings: Optional[np.ndarray] = None
        
        # Load embedding model
        self.model = TextEmbedding(model_name=self.model_name)
        
        # Load data and prepare embeddings
        self._load_and_index()

    def _load_and_index(self):
        """Load recipes from sqlite database and compute/load embeddings."""
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

        ri_map: Dict[str, Dict[str, set]] = {}
        for row in raw_ri:
            rid, orig, c_en, c_ar = row[0], row[1] or "", row[2] or "", row[3] or ""
            if rid not in ri_map:
                ri_map[rid] = {"en": set(), "ar": set()}
            if orig:
                ri_map[rid]["en"].add(orig)
            if c_en:
                ri_map[rid]["en"].add(c_en)
            if c_ar:
                ri_map[rid]["ar"].add(c_ar)

        for r in raw_recipes:
            rid = r[0]
            name_en = r[1] or ""
            name_ar = r[2] or ""
            desc_en = r[3] or ""
            desc_ar = r[4] or ""
            cuisine = r[5] or ""
            category = r[6] or ""
            ings = ri_map.get(rid, {"en": set(), "ar": set()})

            self.recipes[rid] = {
                "recipe_id": rid,
                "name_en": name_en,
                "name_ar": name_ar,
                "desc_en": desc_en,
                "desc_ar": desc_ar,
                "cuisine": cuisine,
                "category": category,
                "ingredients_en": sorted(list(ings["en"])),
                "ingredients_ar": sorted(list(ings["ar"])),
                "is_core": (1 <= int(rid.replace("R", "")) <= 16)
            }
            self.recipe_ids.append(rid)

            ar_ings = ", ".join(sorted(list(ings["ar"])))
            en_ings = ", ".join(sorted(list(ings["en"])))
            doc = (
                f"{name_ar} ({name_en}). التصنيف: {category}، المطبخ: {cuisine}. "
                f"المكونات: {ar_ings}. Ingredients: {en_ings}. "
                f"{desc_ar} {desc_en}"
            )
            self.corpus_docs.append(" ".join(doc.split()))

        # Check disk cache
        if self._is_cache_valid():
            self.embeddings = np.load(str(self.cache_file))
        else:
            self._compute_and_cache_embeddings()

    def _is_cache_valid(self) -> bool:
        """Check if cached embeddings exist and match current corpus size."""
        if self.cache_file.exists():
            try:
                cached = np.load(str(self.cache_file))
                if cached.shape == (len(self.corpus_docs), EMBEDDING_DIM):
                    return True
            except Exception:
                pass
        return False

    def _compute_and_cache_embeddings(self):
        """Compute embeddings using FastEmbed and save to cache."""
        raw_embs = list(self.model.embed(self.corpus_docs))
        arr = np.array(raw_embs, dtype=np.float32)
        # L2-normalize
        norms = np.linalg.norm(arr, axis=1, keepdims=True)
        norms[norms == 0] = 1.0
        self.embeddings = arr / norms

        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            np.save(str(self.cache_file), self.embeddings)
        except Exception:
            pass

    def embed_query(self, query: str) -> np.ndarray:
        """Embed a single query and L2-normalize."""
        q_emb = list(self.model.embed([query]))[0]
        q_vec = np.array(q_emb, dtype=np.float32)
        norm = np.linalg.norm(q_vec)
        if norm > 0:
            q_vec = q_vec / norm
        return q_vec

    def get_similarity_vector(self, query: str) -> np.ndarray:
        """Return a 1D array of cosine similarities for all recipes."""
        q_vec = self.embed_query(query)
        # Dot product with pre-normalized embeddings equals cosine similarity
        sims = np.dot(self.embeddings, q_vec)
        return sims

    def get_all_scores(self, query: str) -> Dict[str, float]:
        """Return a mapping of recipe_id -> cosine similarity score."""
        sims = self.get_similarity_vector(query)
        return {rid: float(sims[i]) for i, rid in enumerate(self.recipe_ids)}

    def search(self, query: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Return top_k recipe matches as [(recipe_id, score), ...]."""
        sims = self.get_similarity_vector(query)
        top_idx = np.argsort(sims)[::-1][:top_k]
        return [(self.recipe_ids[i], float(sims[i])) for i in top_idx]
