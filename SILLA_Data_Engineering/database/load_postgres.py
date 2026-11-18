"""
database/load_postgres.py
=========================
Connects to PostgreSQL 17/18+ on localhost:5432 (silla_db) and loads all processed
datasets with full relational foreign keys, constraints, and indexes.

Usage:
    python database/load_postgres.py
"""

import logging
import os
from pathlib import Path
import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch

ROOT_DIR = Path(__file__).resolve().parent.parent
PROCESSED_DIR = ROOT_DIR / "data" / "processed"
DATA_DIR = ROOT_DIR / "data"
SCHEMA_PG_PATH = ROOT_DIR / "database" / "schema_postgres.sql"

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
logging.basicConfig(level=logging.INFO, format=LOG_FORMAT)
logger = logging.getLogger("load_postgres")

# PostgreSQL Credentials
PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = int(os.getenv("PG_PORT", 5432))
PG_USER = os.getenv("PG_USER", "postgres")
PG_PASSWORD = os.getenv("PG_PASSWORD", "abdallah")
PG_DATABASE = os.getenv("PG_DATABASE", "silla_db")

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


def load_postgres():
    """Connect and populate PostgreSQL silla_db with clean datasets."""
    logger.info("Connecting to PostgreSQL at %s:%s (database: %s) as user '%s' ...",
                PG_HOST, PG_PORT, PG_DATABASE, PG_USER)

    conn = psycopg2.connect(
        host=PG_HOST,
        port=PG_PORT,
        user=PG_USER,
        password=PG_PASSWORD,
        dbname=PG_DATABASE
    )
    conn.autocommit = False
    cursor = conn.cursor()

    try:
        # 1. Execute PostgreSQL Schema
        logger.info("Applying PostgreSQL schema from %s ...", SCHEMA_PG_PATH)
        schema_sql = SCHEMA_PG_PATH.read_text(encoding="utf-8")
        cursor.execute(schema_sql)
        conn.commit()
        logger.info("PostgreSQL schema created successfully.")

        # 2. Insert data_sources
        ds_path = DATA_DIR / "source_registry.csv"
        if ds_path.exists():
            ds_df = pd.read_csv(ds_path, dtype=str, encoding="utf-8-sig").fillna("")
            ds_sql = """
            INSERT INTO data_sources (source_id, source_name, source_type, source_url, access_method, permission_status, collection_date, notes)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (source_id) DO NOTHING;
            """
            ds_rows = [
                (r["source_id"], r["source_name"], r["source_type"], r["source_url"],
                 r["access_method"], r["permission_status"], r["collection_date"], r["notes"])
                for _, r in ds_df.iterrows()
            ]
            execute_batch(cursor, ds_sql, ds_rows)
            logger.info("Ingested %d data_sources into PostgreSQL.", len(ds_rows))

        # 3. Insert stores
        stores_sql = """
        INSERT INTO stores (store_id, store_name, store_url, country, city)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (store_id) DO NOTHING;
        """
        stores_rows = [
            (s["store_id"], s["store_name"], s["store_url"], s["country"], s["city"])
            for s in DEFAULT_STORES
        ]
        execute_batch(cursor, stores_sql, stores_rows)
        logger.info("Ingested %d stores into PostgreSQL.", len(stores_rows))
        store_map = {s["store_name"]: s["store_id"] for s in DEFAULT_STORES}

        # 4. Insert ingredients
        ing_path = PROCESSED_DIR / "ingredients_master.csv"
        ing_df = pd.read_csv(ing_path, dtype=str, encoding="utf-8-sig").fillna("")
        ing_sql = """
        INSERT INTO ingredients (ingredient_id, canonical_name_en, canonical_name_ar, aliases_en, aliases_ar, category, default_unit, dietary_tags)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (ingredient_id) DO NOTHING;
        """
        ing_rows = [
            (r["ingredient_id"], r["canonical_name_en"], r["canonical_name_ar"],
             r["aliases_en"], r["aliases_ar"], r["category"], r["default_unit"], r["dietary_tags"])
            for _, r in ing_df.iterrows()
        ]
        execute_batch(cursor, ing_sql, ing_rows)
        logger.info("Ingested %d canonical ingredients into PostgreSQL.", len(ing_rows))

        # 5. Insert recipes
        rec_path = PROCESSED_DIR / "recipes_clean.csv"
        rec_df = pd.read_csv(rec_path, dtype=str, encoding="utf-8-sig").fillna("")
        rec_sql = """
        INSERT INTO recipes (
            recipe_id, recipe_name_en, recipe_name_ar, description, description_ar,
            cuisine, category, base_servings, prep_time_min,
            cook_time_min, difficulty, instructions, image_url,
            source_url, source_id, collection_date
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (recipe_id) DO NOTHING;
        """
        rec_rows = []
        for _, r in rec_df.iterrows():
            servings = float(r.get("base_servings", 4) or 4)
            prep_t = int(float(r.get("preparation_time", 15) or 15))
            cook_t = int(float(r.get("cooking_time", 25) or 25))
            source_id = r.get("source_id", "SRC002") or "SRC002"
            rec_rows.append((
                r["recipe_id"], r["recipe_name_en"], r["recipe_name_ar"], r.get("description", ""),
                r.get("description_ar", ""),
                r.get("cuisine", "Egyptian"), r.get("category", "Main Course"), servings,
                prep_t, cook_t, r.get("difficulty", "Medium"), r.get("cooking_instructions", ""),
                r.get("image_url", ""), r.get("source_url", ""), source_id, r.get("collection_date", "2026-11-15")
            ))
        execute_batch(cursor, rec_sql, rec_rows)
        logger.info("Ingested %d recipes into PostgreSQL.", len(rec_rows))

        # 6. Insert recipe_ingredients
        ri_path = PROCESSED_DIR / "recipe_ingredients_clean.csv"
        ri_df = pd.read_csv(ri_path, dtype=str, encoding="utf-8-sig").fillna("")
        ri_sql = """
        INSERT INTO recipe_ingredients (
            recipe_ingredient_id, recipe_id, ingredient_id, original_ingredient_name,
            quantity, unit, preparation_note, is_optional, source_url
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (recipe_ingredient_id) DO NOTHING;
        """
        ri_rows = []
        for _, r in ri_df.iterrows():
            qty = float(r["quantity"]) if r["quantity"] else 1.0
            opt = int(float(r["is_optional"])) if r["is_optional"] else 0
            ing_id = r["ingredient_id"] if r["ingredient_id"] else None
            ri_rows.append((
                r["recipe_ingredient_id"], r["recipe_id"], ing_id,
                r["original_ingredient_name"], qty, r["unit"],
                r.get("preparation_note", ""), opt, r.get("source_url", "")
            ))
        execute_batch(cursor, ri_sql, ri_rows)
        logger.info("Ingested %d recipe_ingredients into PostgreSQL.", len(ri_rows))

        # 7. Insert products
        prod_path = PROCESSED_DIR / "products_clean.csv"
        prod_df = pd.read_csv(prod_path, dtype=str, encoding="utf-8-sig").fillna("")
        prod_sql = """
        INSERT INTO products (
            product_id, product_name, product_name_ar, brand,
            ingredient_id, category, package_size, package_unit,
            price_egp, store_id, product_url, image_url,
            availability, collection_date, price_source_type, source_id
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (product_id) DO NOTHING;
        """
        prod_rows = []
        history_rows = []
        for _, r in prod_df.iterrows():
            pkg_size = float(r["package_size"]) if r["package_size"] else 1.0
            price = float(r["price_egp"]) if r["price_egp"] else 0.0
            st_name = r.get("store_name", "Carrefour Egypt")
            st_id = store_map.get(st_name, "STR001")
            ing_id = r["ingredient_id"] if r["ingredient_id"] else None
            src_id = "SRC005"
            coll_date = r.get("collection_date", "2026-11-15")

            prod_rows.append((
                r["product_id"], r["product_name"], r["product_name_ar"], r.get("brand", ""),
                ing_id, r.get("category", "General"), pkg_size, r.get("package_unit", "g"),
                price, st_id, r.get("product_url", ""), r.get("image_url", ""),
                r.get("availability", "in_stock"), coll_date, r.get("price_source_type", "listed_supermarket_catalog"),
                src_id
            ))
            history_rows.append((
                r["product_id"], price, coll_date, src_id
            ))

        execute_batch(cursor, prod_sql, prod_rows)
        logger.info("Ingested %d products into PostgreSQL.", len(prod_rows))

        # 8. Insert product_price_history
        hist_sql = """
        INSERT INTO product_price_history (product_id, price_egp, collection_date, source_id)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (product_id, collection_date) DO NOTHING;
        """
        execute_batch(cursor, hist_sql, history_rows)
        logger.info("Ingested %d initial price points into product_price_history.", len(history_rows))

        conn.commit()
        logger.info("All transactions committed successfully.")

        # Verification
        print("\n" + "=" * 60)
        print("POSTGRESQL INGESTION VERIFICATION SUMMARY (silla_db):")
        print("=" * 60)
        tables = ["data_sources", "stores", "ingredients", "recipes", "recipe_ingredients", "products", "product_price_history"]
        for tbl in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {tbl};")
            cnt = cursor.fetchone()[0]
            print(f"Table '{tbl:<24}': {cnt:>6} rows")

        # Test Sample Join
        join_test = """
        SELECT
            r.recipe_name_en,
            ri.original_ingredient_name,
            p.product_name,
            p.price_egp,
            s.store_name
        FROM recipes r
        JOIN recipe_ingredients ri ON r.recipe_id = ri.recipe_id
        JOIN ingredients i ON ri.ingredient_id = i.ingredient_id
        JOIN products p ON i.ingredient_id = p.ingredient_id
        JOIN stores s ON p.store_id = s.store_id
        WHERE r.recipe_id = 'R0001'
        LIMIT 5;
        """
        cursor.execute(join_test)
        sample_results = cursor.fetchall()
        print("\n" + "-" * 60)
        print("SAMPLE ANALYTICAL JOIN (Recipe R0001 -> Ingredients -> Products):")
        print("-" * 60)
        for res in sample_results:
            print(f"Recipe: {res[0]} | Ing: {res[1]} | Product: {res[2]} | Price: {res[3]} EGP | Store: {res[4]}")
        print("=" * 60)

    except Exception as e:
        conn.rollback()
        logger.error("Error during PostgreSQL ingestion: %s", e)
        raise e
    finally:
        cursor.close()
        conn.close()
        logger.info("PostgreSQL connection closed.")


if __name__ == "__main__":
    load_postgres()
