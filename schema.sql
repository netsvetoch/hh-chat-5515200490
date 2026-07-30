-- Normalized companies schema (data_pack dump)

CREATE TABLE IF NOT EXISTS categories (
    id   SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS cities (
    id   SERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS companies (
    id            TEXT PRIMARY KEY,
    name          TEXT NOT NULL,
    category_id   INTEGER NOT NULL REFERENCES categories (id),
    city_id       INTEGER NOT NULL REFERENCES cities (id),
    address       TEXT,
    rating        NUMERIC(2, 1),
    reviews_count INTEGER NOT NULL DEFAULT 0 CHECK (reviews_count >= 0),
    site          TEXT,
    phone         TEXT,
    loaded_at     TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_companies_category_id ON companies (category_id);
CREATE INDEX IF NOT EXISTS idx_companies_city_id ON companies (city_id);
CREATE INDEX IF NOT EXISTS idx_companies_reviews_count ON companies (reviews_count);
CREATE INDEX IF NOT EXISTS idx_companies_with_site_category
    ON companies (category_id)
    WHERE site IS NOT NULL;
