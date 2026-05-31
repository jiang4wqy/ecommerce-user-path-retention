WITH banded AS (
  SELECT
    CASE
      WHEN price <= 100 THEN '0-100'
      WHEN price <= 300 THEN '100-300'
      WHEN price <= 500 THEN '300-500'
      WHEN price <= 1000 THEN '500-1000'
      ELSE '1000+'
    END AS price_band,
    *
  FROM events_clean
)
SELECT
  price_band,
  COUNT(DISTINCT user_id) AS users,
  SUM(CASE WHEN event_type = 'view' THEN 1 ELSE 0 END) AS views,
  SUM(CASE WHEN event_type = 'cart' THEN 1 ELSE 0 END) AS carts,
  SUM(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END) AS purchases,
  SUM(CASE WHEN event_type = 'purchase' THEN price ELSE 0 END) AS gmv,
  SUM(CASE WHEN event_type = 'cart' THEN 1 ELSE 0 END)::DOUBLE
    / NULLIF(SUM(CASE WHEN event_type = 'view' THEN 1 ELSE 0 END), 0) AS cart_rate,
  SUM(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END)::DOUBLE
    / NULLIF(SUM(CASE WHEN event_type = 'view' THEN 1 ELSE 0 END), 0) AS purchase_rate
FROM banded
GROUP BY price_band
ORDER BY
  CASE price_band
    WHEN '0-100' THEN 1
    WHEN '100-300' THEN 2
    WHEN '300-500' THEN 3
    WHEN '500-1000' THEN 4
    ELSE 5
  END;
