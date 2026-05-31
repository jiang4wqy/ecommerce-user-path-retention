WITH session_flags AS (
  SELECT
    user_session,
    COUNT(*) AS events,
    COUNT(DISTINCT product_id) AS unique_products,
    MAX(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END) AS purchased
  FROM events_clean
  GROUP BY user_session
)
SELECT
  CASE WHEN purchased = 1 THEN 'Purchased' ELSE 'No Purchase' END AS session_type,
  COUNT(DISTINCT user_session) AS sessions,
  AVG(events) AS avg_events_per_session,
  AVG(unique_products) AS avg_products_per_session
FROM session_flags
GROUP BY session_type
ORDER BY session_type;
