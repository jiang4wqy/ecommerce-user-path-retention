-- True funnel: a user/session counts at a step only if every earlier step is
-- also present (view ⊇ cart ⊇ purchase), so step_rate can never exceed 1.
WITH user_steps AS (
  SELECT
    user_id,
    MAX(event_type = 'view')::INT AS did_view,
    MAX(event_type = 'cart')::INT AS did_cart,
    MAX(event_type = 'purchase')::INT AS did_purchase
  FROM events_clean
  GROUP BY user_id
),
session_steps AS (
  SELECT
    user_session,
    MAX(event_type = 'view')::INT AS did_view,
    MAX(event_type = 'cart')::INT AS did_cart,
    MAX(event_type = 'purchase')::INT AS did_purchase
  FROM events_clean
  GROUP BY user_session
),
step_users AS (
  SELECT 'view' AS step, 1 AS step_order,
    (SELECT COUNT(*) FROM user_steps WHERE did_view = 1) AS users,
    (SELECT COUNT(*) FROM session_steps WHERE did_view = 1) AS sessions
  UNION ALL
  SELECT 'cart' AS step, 2 AS step_order,
    (SELECT COUNT(*) FROM user_steps WHERE did_view = 1 AND did_cart = 1) AS users,
    (SELECT COUNT(*) FROM session_steps WHERE did_view = 1 AND did_cart = 1) AS sessions
  UNION ALL
  SELECT 'purchase' AS step, 3 AS step_order,
    (SELECT COUNT(*) FROM user_steps WHERE did_view = 1 AND did_cart = 1 AND did_purchase = 1) AS users,
    (SELECT COUNT(*) FROM session_steps WHERE did_view = 1 AND did_cart = 1 AND did_purchase = 1) AS sessions
)
SELECT
  step,
  users,
  sessions,
  ROUND(users::DOUBLE / NULLIF(FIRST_VALUE(users) OVER (ORDER BY step_order), 0), 4) AS overall_rate,
  COALESCE(ROUND(users::DOUBLE / NULLIF(LAG(users) OVER (ORDER BY step_order), 0), 4), 1.0) AS step_rate
FROM step_users
ORDER BY step_order;
