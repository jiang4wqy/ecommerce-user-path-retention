WITH ordered AS (
  SELECT
    user_session,
    event_type,
    ROW_NUMBER() OVER (PARTITION BY user_session ORDER BY event_time) AS event_rank
  FROM events_clean
),
session_paths AS (
  SELECT
    user_session,
    STRING_AGG(event_type, ' > ' ORDER BY event_rank) AS path
  FROM ordered
  WHERE event_rank <= 5
  GROUP BY user_session
)
SELECT
  path,
  COUNT(*) AS sessions
FROM session_paths
GROUP BY path
ORDER BY sessions DESC
LIMIT 20;
