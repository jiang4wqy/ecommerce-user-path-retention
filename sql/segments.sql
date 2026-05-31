WITH user_flags AS (
  SELECT
    user_id,
    SUM(CASE WHEN event_type = 'view' THEN 1 ELSE 0 END) AS views,
    SUM(CASE WHEN event_type = 'cart' THEN 1 ELSE 0 END) AS carts,
    SUM(CASE WHEN event_type = 'remove_from_cart' THEN 1 ELSE 0 END) AS removes,
    SUM(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END) AS purchases
  FROM events_clean
  GROUP BY user_id
),
segments AS (
  SELECT
    user_id,
    CASE
      WHEN purchases >= 2 THEN 'Repeat Purchasers'
      WHEN purchases >= 1 THEN 'Purchasers'
      WHEN carts >= 1 THEN 'Cart Abandoners'
      ELSE 'Browsers Only'
    END AS segment
  FROM user_flags
)
SELECT
  segment,
  COUNT(DISTINCT user_id) AS users,
  COUNT(DISTINCT user_id)::DOUBLE / SUM(COUNT(DISTINCT user_id)) OVER () AS share
FROM segments
GROUP BY segment
ORDER BY users DESC;
