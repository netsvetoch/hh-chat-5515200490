# Companies → Supabase

Загрузка выгрузки компаний (`data_pack/page_*.json`) в Supabase с нормализованной схемой, дедупликацией и аналитическими SQL-запросами.

## Структура

| Файл               | Описание                                           |
| ------------------ | -------------------------------------------------- |
| `schema.sql`       | DDL: `categories`, `cities`, `companies` + индексы |
| `load_data.py`     | Скрипт загрузки (upsert)                           |
| `queries.sql`      | 3 аналитических запроса                            |
| `data_pack/`       | Исходные JSON (`page_001` … `page_020`)            |
| `requirements.txt` | Python-зависимости                                 |
| `.env.example`     | Пример `DATABASE_URL`                              |

## Схема

- **categories** — справочник категорий (`name` UNIQUE)
- **cities** — справочник городов (`name` UNIQUE)
- **companies** — факты: FK на category/city, PK = внешний `id` (`c_000001` …)

Дедупликация: `ON CONFLICT (id) DO UPDATE` (last-write-wins). Из 1000 строк в dump — **994** уникальных `id`.

## Быстрый старт

```bash
# 1. Зависимости
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Строка подключения (Supabase → Project Settings → Database → URI)
cp .env.example .env
# отредактируйте DATABASE_URL

# 3. Схема
psql "$DATABASE_URL" -f schema.sql

# 4. Данные
export $(grep -v '^#' .env | xargs)
python load_data.py

# 5. Запросы
psql "$DATABASE_URL" -f queries.sql
```

Либо по шагам:

```bash
export DATABASE_URL='postgresql://postgres.[REF]:[PASSWORD]@aws-0-[REGION].pooler.supabase.com:5432/postgres'
psql "$DATABASE_URL" -f schema.sql
python load_data.py
psql "$DATABASE_URL" -f queries.sql
```

## Запросы

1. **Топ-5 категорий** по числу компаний
2. **Средний рейтинг по городам** только для компаний с `reviews_count >= 10`
3. **Доля компаний с сайтом** (`site IS NOT NULL`) по категориям, %

## Supabase-проект

Данные загружены в проект **hh-chat-5515200490** (`ttacqbtybykpviivrdmv`).

## Примечания

- `review.csv` в загрузку не входит (только `page_*.json`)
- `rating`, `site`, `phone` допускают `NULL`
- Индексы: `category_id`, `city_id`, `reviews_count`, partial по `site IS NOT NULL`
