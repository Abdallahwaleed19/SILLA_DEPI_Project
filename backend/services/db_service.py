"""
backend/services/db_service.py
==============================
Database Service for SILLA.
Handles querying the SILLA database cleanly and efficiently.
"""

import sqlite3
import json
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path

from backend.config import DB_PATH


def get_db_connection() -> sqlite3.Connection:
    """Creates a connection to the SQLite database with row factory enabled."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def get_db_stats() -> Dict[str, Any]:
    """Returns row counts and metadata for health checks."""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            stats = {}
            for table in ["recipes", "ingredients", "recipe_ingredients", "products", "stores"]:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                stats[table] = cursor.fetchone()[0]
            return {"connected": True, "type": "sqlite", "counts": stats}
    except Exception as e:
        return {"connected": False, "error": str(e)}


def list_recipes(
    search: Optional[str] = None,
    category: Optional[str] = None,
    cuisine: Optional[str] = None,
    limit: Any = 50,
    offset: Any = 0
) -> Tuple[int, List[Dict[str, Any]]]:
    """
    Lists recipes with optional filters, search, and pagination.
    Returns (total_count, list_of_recipes).
    """
    conditions = []
    params: List[Any] = []

    if search and isinstance(search, str):
        s = f"%{search.strip()}%"
        conditions.append("(recipe_name_en LIKE ? OR recipe_name_ar LIKE ? OR description LIKE ? OR description_ar LIKE ?)")
        params.extend([s, s, s, s])

    if category and isinstance(category, str) and category.lower() != "all":
        conditions.append("LOWER(category) = LOWER(?)")
        params.append(category.strip())

    if cuisine and isinstance(cuisine, str) and cuisine.lower() != "all":
        conditions.append("LOWER(cuisine) = LOWER(?)")
        params.append(cuisine.strip())

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    lim = int(limit) if isinstance(limit, (int, float, str)) and str(limit).isdigit() else 50
    off = int(offset) if isinstance(offset, (int, float, str)) and str(offset).isdigit() else 0

    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Count total
        count_query = f"SELECT COUNT(*) FROM recipes {where_clause}"
        cursor.execute(count_query, params)
        total = cursor.fetchone()[0]

        # Fetch records
        query = f"""
            SELECT 
                recipe_id, recipe_name_en, recipe_name_ar,
                description, description_ar, cuisine, category,
                base_servings, prep_time_min, cook_time_min, difficulty,
                image_url
            FROM recipes
            {where_clause}
            ORDER BY recipe_id ASC
            LIMIT ? OFFSET ?
        """
        cursor.execute(query, params + [lim, off])
        rows = [dict(row) for row in cursor.fetchall()]

    return total, rows


def get_recipe_detail(recipe_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves full details for a recipe, including parsed instructions and ingredients list.
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Recipe header
        cursor.execute("""
            SELECT 
                recipe_id, recipe_name_en, recipe_name_ar,
                description, description_ar, cuisine, category,
                base_servings, prep_time_min, cook_time_min, difficulty,
                instructions, image_url, source_url, source_id
            FROM recipes
            WHERE recipe_id = ?
        """, (recipe_id,))
        row = cursor.fetchone()
        if not row:
            return None

        recipe = dict(row)

        # Parse instructions
        raw_instructions = recipe.get("instructions") or ""
        if isinstance(raw_instructions, str):
            raw_instructions = raw_instructions.strip()
            if raw_instructions.startswith("[") and raw_instructions.endswith("]"):
                try:
                    instructions = json.loads(raw_instructions)
                except Exception:
                    instructions = [s.strip() for s in raw_instructions.split("\n") if s.strip()]
            else:
                lines = [s.strip() for s in raw_instructions.split("\n") if s.strip()]
                if len(lines) <= 1 and ". " in raw_instructions:
                    lines = [s.strip() + "." for s in raw_instructions.split(". ") if s.strip()]
                instructions = lines
        elif isinstance(raw_instructions, list):
            instructions = raw_instructions
        else:
            instructions = [str(raw_instructions)]

        recipe["instructions"] = instructions

        # Fetch ingredients
        cursor.execute("""
            SELECT 
                ri.recipe_ingredient_id,
                ri.recipe_id,
                ri.ingredient_id,
                ri.original_ingredient_name AS original_name,
                ri.quantity,
                ri.unit,
                ri.preparation_note,
                ri.is_optional,
                i.canonical_name_ar,
                i.canonical_name_en,
                i.category AS ingredient_category,
                i.default_unit
            FROM recipe_ingredients ri
            LEFT JOIN ingredients i ON ri.ingredient_id = i.ingredient_id
            WHERE ri.recipe_id = ?
            ORDER BY ri.recipe_ingredient_id ASC
        """, (recipe_id,))
        recipe["ingredients"] = [dict(r) for r in cursor.fetchall()]

    return recipe


def list_ingredients() -> List[Dict[str, Any]]:
    """Lists all canonical ingredients."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ingredient_id, canonical_name_en, canonical_name_ar, category, default_unit, dietary_tags
            FROM ingredients
            ORDER BY canonical_name_ar ASC
        """)
        return [dict(r) for r in cursor.fetchall()]


def list_stores() -> List[Dict[str, Any]]:
    """Lists all available stores."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT store_id, store_name, store_url, country, city
            FROM stores
            ORDER BY store_id ASC
        """)
        return [dict(r) for r in cursor.fetchall()]


def list_products(
    store_id: Optional[str] = None,
    ingredient_id: Optional[str] = None,
    limit: Any = 100,
    offset: Any = 0
) -> List[Dict[str, Any]]:
    """Lists supermarket products with optional filters."""
    conditions = []
    params: List[Any] = []

    if store_id and isinstance(store_id, str):
        conditions.append("store_id = ?")
        params.append(store_id)
    if ingredient_id and isinstance(ingredient_id, str):
        conditions.append("ingredient_id = ?")
        params.append(ingredient_id)

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    lim = int(limit) if isinstance(limit, (int, float, str)) and str(limit).isdigit() else 100
    off = int(offset) if isinstance(offset, (int, float, str)) and str(offset).isdigit() else 0

    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(f"""
            SELECT 
                product_id, product_name, product_name_ar, brand,
                ingredient_id, category, package_size, package_unit,
                price_egp, store_id, availability, image_url
            FROM products
            {where_clause}
            ORDER BY price_egp ASC
            LIMIT ? OFFSET ?
        """, params + [lim, off])
        return [dict(r) for r in cursor.fetchall()]
