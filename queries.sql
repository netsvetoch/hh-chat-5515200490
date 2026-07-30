-- 1. Топ-5 категорий по числу компаний
SELECT
    cat.name AS category,
    COUNT(*) AS companies_count
FROM companies c
JOIN categories cat ON cat.id = c.category_id
GROUP BY cat.id, cat.name
ORDER BY companies_count DESC, cat.name
LIMIT 5;

-- 2. Средний рейтинг по городам среди компаний с 10+ отзывами
SELECT
    ci.name AS city,
    ROUND(AVG(c.rating), 2) AS avg_rating,
    COUNT(*) AS companies_count
FROM companies c
JOIN cities ci ON ci.id = c.city_id
WHERE c.reviews_count >= 10
  AND c.rating IS NOT NULL
GROUP BY ci.id, ci.name
ORDER BY avg_rating DESC, ci.name;

-- 3. Доля компаний с сайтом по категориям
SELECT
    cat.name AS category,
    COUNT(*) AS companies_total,
    COUNT(c.site) AS companies_with_site,
    ROUND(100.0 * COUNT(c.site) / COUNT(*), 2) AS site_share_pct
FROM companies c
JOIN categories cat ON cat.id = c.category_id
GROUP BY cat.id, cat.name
ORDER BY site_share_pct DESC, cat.name;
