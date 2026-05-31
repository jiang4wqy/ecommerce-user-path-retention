from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import pandas as pd


@dataclass(frozen=True)
class EventFilters:
    start_date: date | None = None
    end_date: date | None = None
    categories: tuple[str, ...] = ()
    brands: tuple[str, ...] = ()
    max_price: float | None = None


def filter_events(events: pd.DataFrame, filters: EventFilters) -> pd.DataFrame:
    filtered = events.copy()
    if filters.start_date is not None:
        filtered = filtered[filtered["event_date"] >= filters.start_date]
    if filters.end_date is not None:
        filtered = filtered[filtered["event_date"] <= filters.end_date]
    if filters.categories:
        filtered = filtered[filtered["category_code"].isin(filters.categories)]
    if filters.brands:
        filtered = filtered[filtered["brand"].isin(filters.brands)]
    if filters.max_price is not None:
        filtered = filtered[filtered["price"] <= filters.max_price]
    return filtered.reset_index(drop=True)
