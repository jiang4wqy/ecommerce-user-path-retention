SELECT
  event_date,
  COUNT(DISTINCT user_id) AS dau,
  COUNT(DISTINCT user_session) AS sessions,
  COUNT(*) AS events,
  SUM(CASE WHEN event_type = 'view' THEN 1 ELSE 0 END) AS views,
  SUM(CASE WHEN event_type = 'cart' THEN 1 ELSE 0 END) AS cart_adds,
  SUM(CASE WHEN event_type = 'remove_from_cart' THEN 1 ELSE 0 END) AS cart_removes,
  SUM(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END) AS purchases,
  SUM(CASE WHEN event_type = 'purchase' THEN price ELSE 0 END) AS gmv,
  SUM(CASE WHEN event_type = 'cart' THEN 1 ELSE 0 END)::DOUBLE
    / NULLIF(SUM(CASE WHEN event_type = 'view' THEN 1 ELSE 0 END), 0) AS cart_rate,
  SUM(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END)::DOUBLE
    / NULLIF(SUM(CASE WHEN event_type = 'view' THEN 1 ELSE 0 END), 0) AS purchase_rate
FROM events_clean
GROUP BY event_date
ORDER BY event_date;
