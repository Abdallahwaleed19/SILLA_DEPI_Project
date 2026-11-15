-- =============================================================================
-- SILLA Project — PostgreSQL Production Database Schema
-- Compatible with PostgreSQL 14, 15, 16, 17, and 18+
-- =============================================================================

-- Drop tables in reverse dependency order if recreating
DROP TABLE IF EXISTS product_price_history CASCADE;
DROP TABLE IF EXISTS products CASCADE;
DROP TABLE IF EXISTS recipe_ingredients CASCADE;
DROP TABLE IF EXISTS recipes CASCADE;
DROP TABLE IF EXISTS ingredients CASCADE;
DROP TABLE IF EXISTS stores CASCADE;
DROP TABLE IF EXISTS data_sources CASCADE;

-- -----------------------------------------------------------------------------
-- 1. data_sources
-- -----------------------------------------------------------------------------
CREATE TABLE data_sources (
    source_id         VARCHAR(50) PRIMARY KEY,
    source_name       VARCHAR(255) NOT NULL,
    source_type       VARCHAR(100),
    source_url        TEXT,
    access_method     VARCHAR(100),
    permission_status VARCHAR(100) DEFAULT 'unknown',
    collection_date   VARCHAR(50),
    notes             TEXT
);

-- -----------------------------------------------------------------------------
-- 2. stores
-- -----------------------------------------------------------------------------
CREATE TABLE stores (
    store_id   VARCHAR(50) PRIMARY KEY,
    store_name VARCHAR(255) NOT NULL UNIQUE,
    store_url  TEXT,
    country    VARCHAR(100) DEFAULT 'Egypt',
    city       VARCHAR(150)
);

-- -----------------------------------------------------------------------------
-- 3. ingredients
-- -----------------------------------------------------------------------------
CREATE TABLE ingredients (
    ingredient_id      VARCHAR(50) PRIMARY KEY,
    canonical_name_en  VARCHAR(255) NOT NULL,
    canonical_name_ar  VARCHAR(255),
    aliases_en         TEXT,
    aliases_ar         TEXT,
    category           VARCHAR(100),
    default_unit       VARCHAR(50) DEFAULT 'g',
    dietary_tags       VARCHAR(255)
);

-- -----------------------------------------------------------------------------
-- 4. recipes
-- -----------------------------------------------------------------------------
CREATE TABLE recipes (
    recipe_id       VARCHAR(50) PRIMARY KEY,
    recipe_name_en  VARCHAR(255) NOT NULL,
    recipe_name_ar  VARCHAR(255),
    description     TEXT,
    cuisine         VARCHAR(100),
    category        VARCHAR(100),
    base_servings   NUMERIC DEFAULT 4,
    prep_time_min   INTEGER,
    cook_time_min   INTEGER,
    difficulty      VARCHAR(50),
    instructions    TEXT,
    image_url       TEXT,
    source_url      TEXT,
    source_id       VARCHAR(50) REFERENCES data_sources(source_id) ON DELETE SET NULL,
    collection_date VARCHAR(50)
);

-- -----------------------------------------------------------------------------
-- 5. recipe_ingredients
-- -----------------------------------------------------------------------------
CREATE TABLE recipe_ingredients (
    recipe_ingredient_id     VARCHAR(50) PRIMARY KEY,
    recipe_id                VARCHAR(50) NOT NULL REFERENCES recipes(recipe_id) ON DELETE CASCADE,
    ingredient_id            VARCHAR(50) REFERENCES ingredients(ingredient_id) ON DELETE SET NULL,
    original_ingredient_name VARCHAR(255),
    quantity                 NUMERIC,
    unit                     VARCHAR(50),
    preparation_note         TEXT,
    is_optional              SMALLINT DEFAULT 0,
    source_url               TEXT,
    CONSTRAINT uq_recipe_ingredient UNIQUE (recipe_id, original_ingredient_name)
);

-- -----------------------------------------------------------------------------
-- 6. products
-- -----------------------------------------------------------------------------
CREATE TABLE products (
    product_id         VARCHAR(50) PRIMARY KEY,
    product_name       VARCHAR(255) NOT NULL,
    product_name_ar    VARCHAR(255),
    brand              VARCHAR(150),
    ingredient_id      VARCHAR(50) REFERENCES ingredients(ingredient_id) ON DELETE SET NULL,
    category           VARCHAR(100),
    package_size       NUMERIC,
    package_unit       VARCHAR(50),
    price_egp          NUMERIC(10, 2),
    store_id           VARCHAR(50) REFERENCES stores(store_id) ON DELETE SET NULL,
    product_url        TEXT,
    image_url          TEXT,
    availability       VARCHAR(50) DEFAULT 'in_stock',
    collection_date    VARCHAR(50),
    price_source_type  VARCHAR(150),
    source_id          VARCHAR(50) REFERENCES data_sources(source_id) ON DELETE SET NULL
);

-- -----------------------------------------------------------------------------
-- 7. product_price_history
-- -----------------------------------------------------------------------------
CREATE TABLE product_price_history (
    price_history_id  SERIAL PRIMARY KEY,
    product_id        VARCHAR(50) NOT NULL REFERENCES products(product_id) ON DELETE CASCADE,
    price_egp         NUMERIC(10, 2) NOT NULL,
    collection_date   VARCHAR(50) NOT NULL,
    source_id         VARCHAR(50) REFERENCES data_sources(source_id) ON DELETE SET NULL,
    CONSTRAINT uq_product_date UNIQUE (product_id, collection_date)
);

-- =============================================================================
-- Indexes for Performance & Search Optimization
-- =============================================================================
CREATE INDEX idx_pg_recipe_ingredients_recipe_id ON recipe_ingredients(recipe_id);
CREATE INDEX idx_pg_recipe_ingredients_ingredient_id ON recipe_ingredients(ingredient_id);
CREATE INDEX idx_pg_products_ingredient_id ON products(ingredient_id);
CREATE INDEX idx_pg_products_store_id ON products(store_id);
CREATE INDEX idx_pg_price_history_product_id ON product_price_history(product_id);
CREATE INDEX idx_pg_recipes_cuisine ON recipes(cuisine);
CREATE INDEX idx_pg_recipes_category ON recipes(category);
CREATE INDEX idx_pg_ingredients_category ON ingredients(category);
