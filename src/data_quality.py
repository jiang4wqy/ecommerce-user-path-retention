from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from src.config import EVENTS_PARQUET, REPORTS_DIR
from src.transform import EXPECTED_EVENTS, REQUIRED_COLUMNS


TIME_COLUMNS = ["event_date", "event_hour", "week"]


def validate_events(events: pd.DataFrame) -> dict[str, Any]:
    issues: list[str] = []
    expected_columns = REQUIRED_COLUMNS + TIME_COLUMNS
    missing = [column for column in expected_columns if column not in events.columns]
    if missing:
        issues.append(f"Missing required columns: {', '.join(missing)}")

    if "event_type" in events.columns:
        invalid = sorted(set(events["event_type"].dropna()) - EXPECTED_EVENTS)
        if invalid:
            issues.append(f"Invalid event_type values: {', '.join(invalid)}")

    for column in ["event_time", "event_type", "user_id", "user_session"]:
        if column in events.columns:
            nulls = int(events[column].isna().sum())
            if nulls:
                issues.append(f"{column} contains {nulls} missing values")

    if "price" in events.columns:
        negative_prices = int((pd.to_numeric(events["price"], errors="coerce") < 0).sum())
        if negative_prices:
            issues.append(f"Negative prices: {negative_prices}")

    event_types = (
        events["event_type"].value_counts().to_dict() if "event_type" in events.columns else {}
    )
    date_range = {}
    if "event_date" in events.columns and not events.empty:
        date_range = {
            "min": str(events["event_date"].min()),
            "max": str(events["event_date"].max()),
            "unique_days": int(events["event_date"].nunique()),
        }

    return {
        "status": "pass" if not issues else "fail",
        "rows": int(len(events)),
        "users": int(events["user_id"].nunique()) if "user_id" in events.columns else 0,
        "sessions": int(events["user_session"].nunique())
        if "user_session" in events.columns
        else 0,
        "event_types": event_types,
        "date_range": date_range,
        "issues": issues,
    }


def validate_parquet(path: Path = EVENTS_PARQUET) -> dict[str, Any]:
    return validate_events(pd.read_parquet(path))


def write_quality_report(path: Path = EVENTS_PARQUET) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report = validate_parquet(path)
    output = REPORTS_DIR / "data_quality_report.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return output
