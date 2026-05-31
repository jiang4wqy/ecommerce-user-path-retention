from __future__ import annotations

import pandas as pd


EXPECTED_EVENTS = {"view", "cart", "remove_from_cart", "purchase"}
REQUIRED_COLUMNS = [
    "event_time",
    "event_type",
    "product_id",
    "category_code",
    "brand",
    "price",
    "user_id",
    "user_session",
]


def clean_events(events: pd.DataFrame) -> pd.DataFrame:
    """Keep valid ecommerce behavior events and normalize basic types."""
    missing = [column for column in REQUIRED_COLUMNS if column not in events.columns]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}")

    clean = events.loc[:, REQUIRED_COLUMNS].copy()
    clean = clean.dropna(subset=["event_time", "event_type", "user_id", "user_session"])
    clean = clean[clean["event_type"].isin(EXPECTED_EVENTS)]
    clean["event_time"] = pd.to_datetime(clean["event_time"], utc=True, errors="coerce")
    clean["price"] = pd.to_numeric(clean["price"], errors="coerce").fillna(0.0).clip(lower=0)
    clean["category_code"] = clean["category_code"].fillna("unknown")
    clean["brand"] = clean["brand"].fillna("unknown")
    clean = clean.dropna(subset=["event_time"])
    return clean.reset_index(drop=True)


def add_time_features(events: pd.DataFrame) -> pd.DataFrame:
    """Add date, hour, and week-start fields used by SQL and charts."""
    enriched = events.copy()
    enriched["event_time"] = pd.to_datetime(enriched["event_time"], utc=True, errors="coerce")
    enriched = enriched.dropna(subset=["event_time"]).reset_index(drop=True)
    normalized = enriched["event_time"].dt.normalize()
    enriched["event_date"] = normalized.dt.date
    enriched["event_hour"] = enriched["event_time"].dt.hour
    enriched["week"] = (normalized - pd.to_timedelta(enriched["event_time"].dt.weekday, unit="D")).dt.date
    return enriched
