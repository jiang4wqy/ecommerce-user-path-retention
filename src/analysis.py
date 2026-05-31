from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd

from src.config import EVENTS_PARQUET, SQL_DIR
from src.metrics import (
    _safe_divide,
    build_daily_kpis,
    build_funnel,
    build_retention,
    build_segments,
    build_top_paths,
    purchase_revenue,
)
from src.advanced_analysis import (
    build_cart_abandonment,
    build_price_band_analysis,
    build_purchase_path_comparison,
    build_session_depth,
)


def load_events(path: Path = EVENTS_PARQUET) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(
            f"Missing prepared dataset at {path}. Run: python -m src.prepare_data"
        )
    return pd.read_parquet(path)


def query_sql(sql_file: str, path: Path = EVENTS_PARQUET) -> pd.DataFrame:
    sql_path = SQL_DIR / sql_file
    if not sql_path.exists():
        raise FileNotFoundError(f"Missing SQL file: {sql_path}")
    events = pd.read_parquet(path)
    with duckdb.connect() as con:
        con.register("events_clean", events)
        return con.execute(sql_path.read_text(encoding="utf-8")).df()


def build_all_outputs(events: pd.DataFrame) -> dict[str, pd.DataFrame]:
    return {
        "daily_kpis": build_daily_kpis(events),
        "funnel": build_funnel(events),
        "retention": build_retention(events),
        "paths": build_top_paths(events, top_n=12),
        "segments": build_segments(events),
        "category": build_category_performance(events),
        "price_band": build_price_band_analysis(events),
        "session_depth": build_session_depth(events),
        "cart_abandonment": build_cart_abandonment(events),
        "purchase_paths": build_purchase_path_comparison(events),
    }


def build_category_performance(events: pd.DataFrame, top_n: int = 12) -> pd.DataFrame:
    data = events.assign(_gmv=purchase_revenue(events))
    category = (
        data.groupby("category_code")
        .agg(
            users=("user_id", "nunique"),
            views=("event_type", lambda s: (s == "view").sum()),
            carts=("event_type", lambda s: (s == "cart").sum()),
            purchases=("event_type", lambda s: (s == "purchase").sum()),
            gmv=("_gmv", "sum"),
        )
        .reset_index()
    )
    category = category[category["category_code"].ne("unknown")]
    category["cart_rate"] = _safe_divide(category["carts"], category["views"])
    category["purchase_rate"] = _safe_divide(category["purchases"], category["views"])
    return category.sort_values(["gmv", "purchases"], ascending=False).head(top_n)
