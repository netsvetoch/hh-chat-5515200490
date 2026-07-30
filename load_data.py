#!/usr/bin/env python3
"""Load companies from data_pack/page_*.json into Supabase/Postgres."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

try:
    import psycopg2
    from psycopg2.extras import execute_values
except ImportError:
    print("Install deps: pip install -r requirements.txt", file=sys.stderr)
    raise

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data_pack"


def load_items(data_dir: Path) -> list[dict]:
    items: list[dict] = []
    paths = sorted(data_dir.glob("page_*.json"))
    if not paths:
        raise FileNotFoundError(f"No page_*.json in {data_dir}")
    for path in paths:
        payload = json.loads(path.read_text(encoding="utf-8"))
        batch = payload.get("items") or []
        items.extend(batch)
    return items


def dedupe_by_id(items: list[dict]) -> list[dict]:
    """Keep last occurrence per id (last-write-wins)."""
    by_id: dict[str, dict] = {}
    for item in items:
        company_id = item.get("id")
        if not company_id:
            continue
        by_id[company_id] = item
    return list(by_id.values())


def upsert_dimension(cur, table: str, names: set[str]) -> dict[str, int]:
    if not names:
        return {}
    rows = [(n,) for n in sorted(names)]
    execute_values(
        cur,
        f"INSERT INTO {table} (name) VALUES %s ON CONFLICT (name) DO NOTHING",
        rows,
    )
    cur.execute(f"SELECT id, name FROM {table} WHERE name = ANY(%s)", (list(names),))
    return {name: pk for pk, name in cur.fetchall()}


def upsert_companies(cur, companies: list[dict], cat_map: dict[str, int], city_map: dict[str, int]) -> int:
    rows = []
    for c in companies:
        rows.append(
            (
                c["id"],
                c["name"],
                cat_map[c["category"]],
                city_map[c["city"]],
                c.get("address"),
                c.get("rating"),
                int(c.get("reviews_count") or 0),
                c.get("site"),
                c.get("phone"),
            )
        )
    sql = """
        INSERT INTO companies (
            id, name, category_id, city_id, address, rating, reviews_count, site, phone
        ) VALUES %s
        ON CONFLICT (id) DO UPDATE SET
            name = EXCLUDED.name,
            category_id = EXCLUDED.category_id,
            city_id = EXCLUDED.city_id,
            address = EXCLUDED.address,
            rating = EXCLUDED.rating,
            reviews_count = EXCLUDED.reviews_count,
            site = EXCLUDED.site,
            phone = EXCLUDED.phone,
            loaded_at = now()
    """
    execute_values(cur, sql, rows, page_size=200)
    return len(rows)


def main() -> int:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("Set DATABASE_URL (Postgres connection string).", file=sys.stderr)
        return 1

    data_dir = Path(os.environ.get("DATA_DIR", DATA_DIR))
    raw = load_items(data_dir)
    companies = dedupe_by_id(raw)
    print(f"Loaded {len(raw)} rows from JSON, {len(companies)} unique by id")

    categories = {c["category"] for c in companies if c.get("category")}
    cities = {c["city"] for c in companies if c.get("city")}

    conn = psycopg2.connect(database_url)
    try:
        with conn:
            with conn.cursor() as cur:
                cat_map = upsert_dimension(cur, "categories", categories)
                city_map = upsert_dimension(cur, "cities", cities)
                n = upsert_companies(cur, companies, cat_map, city_map)
                cur.execute("SELECT COUNT(*) FROM companies")
                total = cur.fetchone()[0]
        print(f"Upserted {n} companies; table count = {total}")
        print(f"Categories: {len(cat_map)}, cities: {len(city_map)}")
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
