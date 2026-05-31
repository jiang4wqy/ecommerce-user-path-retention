WITH ordered AS (
  SELECT
    user_session,
    event_type,
    ROW_NUMBER() OVER (PARTITION BY user_session ORDER BY event_time) AS event_rank,
    MAX(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END) OVER (PARTITION BY user_session) AS purchased
  FROM events_clean
),
session_paths AS (
  SELECT
    user_session,
    CASE WHEN MAX(purchased) = 1 THEN 'Purchased' ELSE 'No Purchase' END AS session_type,
    STRING_AGG(event_type, ' > ' ORDER BY event_rank) AS path
  FROM ordered
  WHERE event_rank <= 5
  GROUP BY user_session
)
SELECT
  session_type,
  path,
  COUNT(DISTINCT user_session) AS sessions
FROM session_paths
GROUP BY session_type, path
ORDER BY session_type, sessions DESC
LIMIT 30;
