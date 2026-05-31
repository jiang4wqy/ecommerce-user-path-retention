from __future__ import annotations

from pathlib import Path

import duckdb
import pandas as pd

from src.config import EVENTS_PARQUET, SQL_DIR


SQL_TABLES = {
    "daily_kpis": "daily_kpis.sql",
    "funnel": "funnel.sql",
    "retention": "retention.sql",
    "paths": "paths.sql",
    "segments": "segments.sql",
    "category_performance": "category_performance.sql",
    "price_band_analysis": "price_band_analysis.sql",
    "session_depth": "session_depth.sql",
    "purchase_path_comparison": "purchase_path_comparison.sql",
}


class MetricStore:
    def __init__(self, events_path: Path = EVENTS_PARQUET):
        self.events_path = Path(events_path)

    def table(self, table_name: str) -> pd.DataFrame:
        if table_name == "events_clean":
            return pd.read_parquet(self.events_path)
        if table_name not in SQL_TABLES:
            raise KeyError(f"Unknown metric table: {table_name}")
        sql_path = SQL_DIR / SQL_TABLES[table_name]
        if not sql_path.exists():
            raise FileNotFoundError(f"Missing SQL file: {sql_path}")
        with duckdb.connect() as con:
            con.register("events_clean", pd.read_parquet(self.events_path))
            return con.execute(sql_path.read_text(encoding="utf-8")).df()

    def all_tables(self) -> dict[str, pd.DataFrame]:
        return {name: self.table(name) for name in SQL_TABLES if (SQL_DIR / SQL_TABLES[name]).exists()}
