"""The dashboard runs on the pandas metric builders while the SQL layer is a
parallel implementation. These tests pin the two together so they cannot drift:
the headline funnel and retention metrics must match exactly."""
from __future__ import annotations

import pandas as pd
from pandas.testing import assert_frame_equal

from src.metric_store import MetricStore
from src.metrics import build_funnel, build_retention
from src.transform import add_time_features


def _event(day, hour, etype, user, session):
    return {
        "event_time": f"2019-11-{day:02d}T{hour:02d}:00:00.000Z",
        "event_type": etype,
        "product_id": 1,
        "category_code": "electronics.smartphone",
        "brand": "xiaomi",
        "price": 100.0,
        "user_id": user,
        "user_session": session,
    }


def _parity_events():
    return pd.DataFrame(
        [
            # user 1: full journey on D0, returns on D1 (new session)
            _event(1, 9, "view", 1, "a"),
            _event(1, 9, "cart", 1, "a"),
            _event(1, 10, "purchase", 1, "a"),
            _event(2, 9, "view", 1, "b"),
            # user 2: view + cart, no purchase
            _event(1, 11, "view", 2, "c"),
            _event(1, 11, "cart", 2, "c"),
            # user 3: cart + purchase but never viewed (subset-semantics check)
            _event(1, 12, "cart", 3, "d"),
            _event(1, 12, "purchase", 3, "d"),
        ]
    )


def _store(tmp_path):
    path = tmp_path / "events.parquet"
    add_time_features(_parity_events()).to_parquet(path, index=False)
    return MetricStore(path), pd.read_parquet(path)


def _normalize(df):
    out = df.copy()
    if "cohort_date" in out.columns:
        out["cohort_date"] = out["cohort_date"].astype(str)
    return out.reset_index(drop=True)


def test_funnel_sql_matches_pandas(tmp_path):
    store, events = _store(tmp_path)
    sql = _normalize(store.table("funnel"))
    pandas = _normalize(build_funnel(events))
    assert_frame_equal(sql[pandas.columns], pandas, check_dtype=False)


def test_retention_sql_matches_pandas(tmp_path):
    store, events = _store(tmp_path)
    sql = _normalize(store.table("retention").sort_values(["cohort_date", "days_since_first"]))
    pandas = _normalize(build_retention(events).sort_values(["cohort_date", "days_since_first"]))
    assert_frame_equal(sql[pandas.columns], pandas, check_dtype=False)
