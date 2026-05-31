from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd

from src.config import HF_DATASET, HF_ROWS_API, RAW_DIR


PARQUET_BASE = (
    "https://huggingface.co/datasets/{dataset}/resolve/"
    "refs%2Fconvert%2Fparquet/default/partial-train/{name}"
)
PARQUET_CACHE = RAW_DIR / "parquet_cache"


def hf_parquet_urls(dataset: str = HF_DATASET, num_files: int = 10) -> list[str]:
    return [
        PARQUET_BASE.format(dataset=dataset, name=f"{i:04d}.parquet")
        for i in range(num_files)
    ]


def _download_with_resume(url: str, dest: Path, retries: int = 30, chunk: int = 1 << 20) -> Path:
    """Stream a file to ``dest``, resuming via HTTP Range after interruptions.

    The public parquet shards are ~200 MB each; on a slow/flaky link a single
    GET often drops mid-transfer, so we resume from the bytes already on disk
    instead of restarting. A completed file (size matches Content-Length) is
    reused as-is, which makes re-running the sampler cheap.
    """
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urlopen(Request(url, method="HEAD"), timeout=60) as resp:
        total = int(resp.headers.get("Content-Length", 0))

    for attempt in range(retries):
        have = dest.stat().st_size if dest.exists() else 0
        if total and have >= total:
            return dest
        try:
            request = Request(url, headers={"Range": f"bytes={have}-"} if have else {})
            with urlopen(request, timeout=120) as resp:
                mode = "wb" if have and resp.status == 200 else "ab"  # server may ignore Range
                with open(dest, mode) as handle:
                    while True:
                        block = resp.read(chunk)
                        if not block:
                            break
                        handle.write(block)
        except (URLError, TimeoutError, OSError):
            time.sleep(2 + attempt)
    have = dest.stat().st_size if dest.exists() else 0
    if total and have < total:
        raise RuntimeError(f"Incomplete download for {url}: {have}/{total} bytes")
    return dest


def fetch_user_sample(
    target_rows: int, dataset: str = HF_DATASET, num_files: int = 10
) -> pd.DataFrame:
    """Sample whole users from the public parquet mirror.

    Picks ~1/mod of users via ``hash(user_id) % mod`` and keeps every event for
    them, so sessions stay intact and span the full date range. This is the key
    difference from offset sampling, which slices the time-ordered log and
    shreds individual sessions/journeys. Shards are cached locally first so the
    DuckDB scan runs offline and is not exposed to mid-scan network drops.
    """
    import duckdb

    local_files = [
        str(_download_with_resume(url, PARQUET_CACHE / f"{i:04d}.parquet")).replace("\\", "/")
        for i, url in enumerate(hf_parquet_urls(dataset, num_files))
    ]
    array_sql = "[" + ", ".join(f"'{path}'" for path in local_files) + "]"
    con = duckdb.connect()
    total = con.execute(f"SELECT COUNT(*) FROM read_parquet({array_sql})").fetchone()[0]
    mod = max(1, round(total / max(target_rows, 1)))
    query = f"SELECT * FROM read_parquet({array_sql}) WHERE hash(user_id) % {mod} = 0"
    return con.execute(query).df()


@dataclass(frozen=True)
class HuggingFaceRowsSource:
    dataset: str = HF_DATASET
    config: str = "default"
    split: str = "train"
    page_size: int = 100
    retries: int = 3

    def fetch_page(self, offset: int, length: int | None = None) -> list[dict]:
        query = urlencode(
            {
                "dataset": self.dataset,
                "config": self.config,
                "split": self.split,
                "offset": offset,
                "length": length or self.page_size,
            }
        )
        last_error: Exception | None = None
        for attempt in range(self.retries):
            try:
                with urlopen(f"{HF_ROWS_API}?{query}", timeout=30) as response:
                    payload = json.load(response)
                return [item["row"] for item in payload["rows"]]
            except (URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
                # Retry only transient network/parse failures; let genuine bugs
                # (e.g. a changed payload shape raising KeyError) surface.
                last_error = exc
                time.sleep(1 + attempt)
        raise RuntimeError(f"Failed to fetch dataset page at offset {offset}") from last_error

    def fetch_rows(self, offsets: list[int], rows: int) -> pd.DataFrame:
        if not offsets:
            raise ValueError("offsets must contain at least one starting offset")
        if rows <= 0:
            return pd.DataFrame()

        collected: list[dict] = []
        offset_index = 0
        while len(collected) < rows:
            base_offset = offsets[offset_index % len(offsets)]
            cycle = offset_index // len(offsets)
            offset = base_offset + cycle * self.page_size
            length = min(self.page_size, rows - len(collected))
            page_rows = self.fetch_page(offset, length)
            if not page_rows:
                raise RuntimeError(f"No rows returned from dataset page at offset {offset}")
            collected.extend(page_rows)
            offset_index += 1
        return pd.DataFrame(collected)
