SELECT
  category_code,
  COUNT(DISTINCT user_id) AS users,
  SUM(CASE WHEN event_type = 'view' THEN 1 ELSE 0 END) AS views,
  SUM(CASE WHEN event_type = 'cart' THEN 1 ELSE 0 END) AS carts,
  SUM(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END) AS purchases,
  SUM(CASE WHEN event_type = 'purchase' THEN price ELSE 0 END) AS gmv,
  SUM(CASE WHEN event_type = 'cart' THEN 1 ELSE 0 END)::DOUBLE
    / NULLIF(SUM(CASE WHEN event_type = 'view' THEN 1 ELSE 0 END), 0) AS cart_rate,
  SUM(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END)::DOUBLE
    / NULLIF(SUM(CASE WHEN event_type = 'view' THEN 1 ELSE 0 END), 0) AS purchase_rate
FROM events_clean
WHERE category_code <> 'unknown'
GROUP BY category_code
ORDER BY gmv DESC, purchases DESC
LIMIT 20;
