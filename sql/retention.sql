-- Cohort retention. Day 0 is the cohort itself (always 100%) and is excluded.
-- A full cohort_date x {1,3,7} grid is emitted with zero-filled gaps so the
-- output matches src.metrics.build_retention exactly (heatmap shows 0% cells).
WITH user_dates AS (
  SELECT DISTINCT user_id, event_date
  FROM events_clean
),
first_seen AS (
  SELECT user_id, MIN(event_date) AS cohort_date
  FROM user_dates
  GROUP BY user_id
),
retained AS (
  SELECT
    f.cohort_date,
    DATE_DIFF('day', f.cohort_date::DATE, d.event_date::DATE) AS days_since_first,
    d.user_id
  FROM user_dates d
  JOIN first_seen f USING (user_id)
),
cohort_sizes AS (
  SELECT cohort_date, COUNT(DISTINCT user_id) AS cohort_size
  FROM first_seen
  GROUP BY cohort_date
),
day_grid AS (
  SELECT * FROM (VALUES (1), (3), (7)) AS t(days_since_first)
),
grid AS (
  SELECT c.cohort_date, g.days_since_first, c.cohort_size
  FROM cohort_sizes c
  CROSS JOIN day_grid g
),
counts AS (
  SELECT cohort_date, days_since_first, COUNT(DISTINCT user_id) AS retained_users
  FROM retained
  WHERE days_since_first IN (1, 3, 7)
  GROUP BY cohort_date, days_since_first
)
SELECT
  grid.cohort_date,
  grid.days_since_first,
  COALESCE(counts.retained_users, 0) AS retained_users,
  grid.cohort_size,
  ROUND(COALESCE(counts.retained_users, 0)::DOUBLE / NULLIF(grid.cohort_size, 0), 4) AS retention_rate
FROM grid
LEFT JOIN counts USING (cohort_date, days_since_first)
ORDER BY grid.cohort_date, grid.days_since_first;
