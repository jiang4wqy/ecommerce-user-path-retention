from __future__ import annotations

import argparse
from pathlib import Path

import duckdb

from src.config import DATA_DIR, EVENTS_PARQUET
from src.metric_store import SQL_TABLES


DEFAULT_DB_PATH = DATA_DIR / "processed" / "analytics.duckdb"


def build_database(events_path: Path = EVENTS_PARQUET, db_path: Path = DEFAULT_DB_PATH) -> Path:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    if db_path.exists():
        db_path.unlink()
    with duckdb.connect(str(db_path)) as con:
        con.execute("CREATE TABLE events_clean AS SELECT * FROM read_parquet(?)", [str(events_path)])
        for table_name, sql_file in SQL_TABLES.items():
            sql_path = Path(__file__).resolve().parents[1] / "sql" / sql_file
            if not sql_path.exists():
                continue
            con.execute(f"CREATE TABLE {table_name} AS {sql_path.read_text(encoding='utf-8')}")
    return db_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Build DuckDB analytics database.")
    parser.add_argument("--events", type=Path, default=EVENTS_PARQUET)
    parser.add_argument("--output", type=Path, default=DEFAULT_DB_PATH)
    args = parser.parse_args()
    output = build_database(args.events, args.output)
    print(f"Built analytics database: {output}")


if __name__ == "__main__":
    main()
