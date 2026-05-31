from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pandas as pd

from src.config import PROCESSED_DIR, REPORTS_DIR

WEB_DATA_PATH = Path(__file__).resolve().parents[1] / "web" / "src" / "data" / "metrics.json"
METRIC_FILES = [
    "daily_kpis", "funnel", "retention", "paths", "purchase_paths",
    "segments", "session_depth", "category", "price_band", "cart_abandonment",
]


def _read_insights(insights_path: Path) -> list[str]:
    if not insights_path.exists():
        return []
    return [
        line[2:].strip()
        for line in insights_path.read_text(encoding="utf-8").splitlines()
        if line.startswith("- ")
    ]


def build_web_payload(
    metrics_dir: Path = PROCESSED_DIR / "metrics",
    quality_path: Path = REPORTS_DIR / "data_quality_report.json",
    insights_path: Path = REPORTS_DIR / "insights.md",
) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for name in METRIC_FILES:
        csv_path = metrics_dir / f"{name}.csv"
        payload[name] = pd.read_csv(csv_path).to_dict("records") if csv_path.exists() else []
    quality = json.loads(quality_path.read_text(encoding="utf-8")) if quality_path.exists() else {}
    payload["scope"] = {
        "rows": quality.get("rows", 0),
        "users": quality.get("users", 0),
        "sessions": quality.get("sessions", 0),
        "date_range": quality.get("date_range", {}),
    }
    payload["insights"] = _read_insights(insights_path)
    return payload


def write_web_payload(path: Path = WEB_DATA_PATH) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = build_web_payload()
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


if __name__ == "__main__":
    out = write_web_payload()
    print(f"Wrote web data: {out}")
