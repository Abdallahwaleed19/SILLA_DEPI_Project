"""
database/import_data.py
========================
Imports all processed datasets into SQLite (database/silla.db or custom db_path)
with strict foreign key validation using standard library.

Tables imported in topological order:
1. data_sources  <- data/source_registry.csv
2. stores        <- Standard Egyptian retail chains
3. ingredients   <- data/processed/ingredients_master.csv
4. recipes       <- data/processed/recipes_clean.csv
5. recipe_ingredients <- data/processed/recipe_ingredients_clean.csv
6. products      <- data/processed/products_clean.csv
7. product_price_history <- seeded from initial products collection
"""

import csv
import logging
import sqlite3
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config.settings import (
    DB_PATH, SCHEMA_PATH, PROCESSED_DIR, DATA_DIR,
    LOG_FORMAT, LOG_DATE_FORMAT
)

logging.basicConfig(level="INFO", format=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
logger = logging.getLogger(__name__)

# Standard Egyptian Stores Catalog
DEFAULT_STORES = [
    {"store_id": "STR001", "store_name": "Carrefour Egypt", "store_url": "https://www.carrefouregypt.com", "country": "Egypt", "city": "Cairo/Giza/Alexandria"},
    {"store_id": "STR002", "store_name": "Lulu Hypermarket", "store_url": "https://www.luluhypermarket.com", "country": "Egypt", "city": "Cairo/Giza"},
    {"store_id": "STR003", "store_name": "Hyperone Egypt", "store_url": "https://hyperone.com.eg", "country": "Egypt", "city": "Giza/Sheikh Zayed"},
    {"store_id": "STR004", "store_name": "Seoudi Market", "store_url": "https://seoudimarket.com", "country": "Egypt", "city": "Greater Cairo"},
    {"store_id": "STR005", "store_name": "Gourmet Egypt", "store_url": "https://gourmetegypt.com", "country": "Egypt", "city": "Cairo/Alexandria"},
    {"store_id": "STR006", "store_name": "Local Fresh Market", "store_url": "", "country": "Egypt", "city": "Local Egyptian Markets"},
    {"store_id": "STR007", "store_name": "Coastal Fisheries", "store_url": "", "country": "Egypt", "city": "Alexandria/Suez"},
    {"store_id": "STR008", "store_name": "Gourmet Butchery", "store_url": "https://gourmetegypt.com", "country": "Egypt", "city": "Cairo"}
]


def _load_csv(path: Path) -> list[dict] | None:
    if not path.exists():
        logger.warning("File not found, skipping: %s", path)
        return None
    with open(path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = []
        for r in reader:
            clean_row = {k: (v.strip() if isinstance(v, str) and v.strip() != "" and v.strip().lower() != "nan" else None) for k, v in r.items()}
            rows.append(clean_row)
    logger.info("Loaded %d rows from %s", len(rows), path)
    return rows


def _import_rows(conn: sqlite3.Connection, rows: list[dict], table: str, keep_cols: list[str]) -> int:
    """Insert rows into table, ignoring duplicates."""
    if not rows:
        return 0
    cursor = conn.cursor()
    placeholders = ", ".join(["?"] * len(keep_cols))
    sql = f"INSERT OR IGNORE INTO {table} ({', '.join(keep_cols)}) VALUES ({placeholders})"
    
    tuples = []
    for r in rows:
        t = tuple(r.get(c) for c in keep_cols)
        tuples.append(t)
    
    cursor.executemany(sql, tuples)
    conn.commit()
    logger.info("Successfully imported %d rows -> %s", len(tuples), table)
    return len(tuples)


def import_all(db_path: Path = DB_PATH) -> dict:
    """Run complete database import and verify relationships."""
    if not db_path.exists():
        logger.info("Database not found. Initializing schema from %s ...", SCHEMA_PATH)
        from database.create_database import create_database
        create_database(db_path)

    stats = {}

    with sqlite3.connect(db_path) as conn:
        conn.execute("PRAGMA foreign_keys = ON;")

        # 1. data_sources
        ds_path = DATA_DIR / "source_registry.csv"
        ds_rows = _load_csv(ds_path)
        if ds_rows:
            keep_ds = ["source_id", "source_name", "source_type", "source_url", "access_method", "permission_status", "collection_date", "notes"]
            _import_rows(conn, ds_rows, "data_sources", keep_ds)

        # 2. stores
        keep_stores = ["store_id", "store_name", "store_url", "country", "city"]
        _import_rows(conn, DEFAULT_STORES, "stores", keep_stores)

        # Build store_name -> store_id map
        store_map = {s["store_name"]: s["store_id"] for s in DEFAULT_STORES}

        # 3. ingredients
        ing_path = PROCESSED_DIR / "ingredients_master.csv"
        ing_rows = _load_csv(ing_path)
        if ing_rows:
            keep_ing = ["ingredient_id", "canonical_name_en", "canonical_name_ar", "aliases_en", "aliases_ar", "category", "default_unit", "dietary_tags"]
            _import_rows(conn, ing_rows, "ingredients", keep_ing)

        # 4. recipes
        rec_path = PROCESSED_DIR / "recipes_clean.csv"
        rec_raw_rows = _load_csv(rec_path)
        if rec_raw_rows:
            prepared_rec = []
            for r in rec_raw_rows:
                row_copy = r.copy()
                if not row_copy.get("source_id"):
                    row_copy["source_id"] = "SRC002"
                # Renaming
                row_copy["prep_time_min"] = row_copy.pop("preparation_time", None)
                row_copy["cook_time_min"] = row_copy.pop("cooking_time", None)
                row_copy["instructions"] = row_copy.pop("cooking_instructions", None)
                # Numeric conversions
                try:
                    row_copy["base_servings"] = float(row_copy["base_servings"]) if row_copy.get("base_servings") is not None else 4.0
                except (ValueError, TypeError):
                    row_copy["base_servings"] = 4.0
                try:
                    row_copy["prep_time_min"] = int(float(row_copy["prep_time_min"])) if row_copy.get("prep_time_min") is not None else 15
                except (ValueError, TypeError):
                    row_copy["prep_time_min"] = 15
                try:
                    row_copy["cook_time_min"] = int(float(row_copy["cook_time_min"])) if row_copy.get("cook_time_min") is not None else 20
                except (ValueError, TypeError):
                    row_copy["cook_time_min"] = 20
                prepared_rec.append(row_copy)

            keep_rec = [
                "recipe_id", "recipe_name_en", "recipe_name_ar", "description", "description_ar",
                "cuisine", "category", "base_servings", "prep_time_min",
                "cook_time_min", "difficulty", "instructions", "image_url",
                "source_url", "source_id", "collection_date"
            ]
            _import_rows(conn, prepared_rec, "recipes", keep_rec)

        # 5. recipe_ingredients
        ri_path = PROCESSED_DIR / "recipe_ingredients_clean.csv"
        ri_raw_rows = _load_csv(ri_path)
        if ri_raw_rows:
            prepared_ri = []
            for r in ri_raw_rows:
                row_copy = r.copy()
                try:
                    row_copy["quantity"] = float(row_copy["quantity"]) if row_copy.get("quantity") is not None else 1.0
                except (ValueError, TypeError):
                    row_copy["quantity"] = 1.0
                try:
                    row_copy["is_optional"] = int(float(row_copy["is_optional"])) if row_copy.get("is_optional") is not None else 0
                except (ValueError, TypeError):
                    row_copy["is_optional"] = 0
                prepared_ri.append(row_copy)

            keep_ri = ["recipe_id", "ingredient_id", "original_ingredient_name", "quantity", "unit", "preparation_note", "is_optional"]
            _import_rows(conn, prepared_ri, "recipe_ingredients", keep_ri)

        # 6. products
        prod_path = PROCESSED_DIR / "products_clean.csv"
        prod_raw_rows = _load_csv(prod_path)
        if prod_raw_rows:
            prepared_prod = []
            for r in prod_raw_rows:
                row_copy = r.copy()
                store_name = row_copy.get("store_name", "")
                if not row_copy.get("store_id"):
                    row_copy["store_id"] = store_map.get(store_name, "STR001")
                if not row_copy.get("source_id"):
                    row_copy["source_id"] = "SRC005"
                try:
                    row_copy["package_size"] = float(row_copy["package_size"]) if row_copy.get("package_size") is not None else 1.0
                except (ValueError, TypeError):
                    row_copy["package_size"] = 1.0
                try:
                    row_copy["price_egp"] = float(row_copy["price_egp"]) if row_copy.get("price_egp") is not None else 0.0
                except (ValueError, TypeError):
                    row_copy["price_egp"] = 0.0
                prepared_prod.append(row_copy)

            keep_prod = [
                "product_id", "product_name", "product_name_ar", "brand",
                "ingredient_id", "category", "package_size", "package_unit",
                "price_egp", "store_id", "product_url", "image_url",
                "availability", "collection_date", "price_source_type", "source_id"
            ]
            _import_rows(conn, prepared_prod, "products", keep_prod)

            # 7. product_price_history
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM product_price_history")
            if cursor.fetchone()[0] == 0:
                history_rows = [
                    (row["product_id"], float(row["price_egp"]), row["collection_date"], row["source_id"])
                    for row in prepared_prod
                ]
                cursor.executemany(
                    "INSERT INTO product_price_history (product_id, price_egp, collection_date, source_id) VALUES (?, ?, ?, ?)",
                    history_rows
                )
                conn.commit()
                logger.info("Imported %d initial price points -> product_price_history", len(history_rows))

        # Check table counts
        cursor = conn.cursor()
        tables = ["data_sources", "stores", "ingredients", "recipes", "recipe_ingredients", "products", "product_price_history"]
        for tbl in tables:
            cnt = cursor.execute(f"SELECT COUNT(*) FROM {tbl}").fetchone()[0]
            stats[tbl] = cnt
            logger.info("Table '%s': %d rows verified", tbl, cnt)

        # Foreign Key check
        fk_errors = cursor.execute("PRAGMA foreign_key_check;").fetchall()
        if fk_errors:
            logger.error("Foreign key violations found: %s", fk_errors)
        else:
            logger.info("PRAGMA foreign_key_check PASSED with zero violations.")

    return stats


if __name__ == "__main__":
    import_all()
