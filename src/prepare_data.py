from __future__ import annotations

import argparse
from io import StringIO
from pathlib import Path
from urllib.request import urlopen

import pandas as pd

from src.config import (
    EVENTS_CSV,
    EVENTS_PARQUET,
    PROCESSED_DIR,
)
from src.data_source import HuggingFaceRowsSource, fetch_user_sample
from src.transform import add_time_features, clean_events


def read_source(source: str, rows: int) -> pd.DataFrame:
    """Read a reproducible sample from a public or local source."""
    if source == "hf_users":
        return fetch_user_sample(rows)
    if source == "hf_rows":
        return read_huggingface_rows(rows)
    if source.startswith(("http://", "https://")):
        lines: list[str] = []
        with urlopen(source, timeout=60) as response:
            for line_number, raw_line in enumerate(response):
                if line_number > rows:
                    break
                lines.append(raw_line.decode("utf-8", errors="replace"))
        return pd.read_csv(StringIO("".join(lines)))
    return pd.read_csv(source, nrows=rows)


def read_huggingface_rows(rows: int, page_size: int = 100) -> pd.DataFrame:
    """Read public rows with a mix of contiguous and time-spread pages."""
    source = HuggingFaceRowsSource(page_size=page_size)
    contiguous_rows = min(rows // 2, 3_000)
    collected = source.fetch_rows(list(range(0, contiguous_rows, page_size)) or [0], contiguous_rows)
    collected_rows = collected.to_dict("records")

    spread_offsets = [
        100_000,
        500_000,
        1_000_000,
        2_000_000,
        4_000_000,
        6_000_000,
        8_000_000,
        10_000_000,
        14_000_000,
        18_000_000,
        22_000_000,
        26_000_000,
        30_000_000,
        34_000_000,
    ]
    remaining = max(rows - len(collected_rows), 0)
    if remaining:
        spread = source.fetch_rows(spread_offsets, remaining)
        collected_rows.extend(spread.to_dict("records"))
    return pd.DataFrame(collected_rows)


def prepare_events(source: str, rows: int) -> pd.DataFrame:
    raw = read_source(source, rows)
    clean = clean_events(raw)
    enriched = add_time_features(clean)
    return enriched


def write_outputs(events: pd.DataFrame, parquet_path: Path, csv_path: Path) -> None:
    parquet_path.parent.mkdir(parents=True, exist_ok=True)
    events.to_parquet(parquet_path, index=False)
    events.to_csv(csv_path, index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare ecommerce behavior event sample.")
    parser.add_argument(
        "--source",
        default="hf_users",
        help="Use 'hf_users' (whole-user sample), 'hf_rows', a remote CSV URL, or a local CSV path",
    )
    parser.add_argument(
        "--rows", type=int, default=40_000, help="Approximate target rows to sample from the source"
    )
    parser.add_argument("--parquet", type=Path, default=EVENTS_PARQUET)
    parser.add_argument("--csv", type=Path, default=EVENTS_CSV)
    args = parser.parse_args()

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    events = prepare_events(args.source, args.rows)
    write_outputs(events, args.parquet, args.csv)
    print(f"Prepared {len(events):,} clean events")
    print(f"Parquet: {args.parquet}")
    print(f"CSV sample: {args.csv}")


if __name__ == "__main__":
    main()
