from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
SQL_DIR = PROJECT_ROOT / "sql"
REPORTS_DIR = PROJECT_ROOT / "reports"

DEFAULT_DATA_URL = (
    "https://huggingface.co/datasets/kevykibbz/"
    "ecommerce-behavior-data-from-multi-category-store_oct-nov_2019/"
    "resolve/main/ecommerce-behavior-data-from-multi-category-store_oct-nov_2019.csv"
)
HF_ROWS_API = "https://datasets-server.huggingface.co/rows"
HF_DATASET = "kevykibbz/ecommerce-behavior-data-from-multi-category-store_oct-nov_2019"

EVENTS_PARQUET = PROCESSED_DIR / "events_sample.parquet"
EVENTS_CSV = PROCESSED_DIR / "events_sample.csv"
