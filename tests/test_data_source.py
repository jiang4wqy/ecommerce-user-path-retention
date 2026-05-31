from __future__ import annotations

import pytest

from src.data_source import HuggingFaceRowsSource


def test_fetch_rows_rejects_empty_offset_list():
    source = HuggingFaceRowsSource()

    with pytest.raises(ValueError, match="offsets"):
        source.fetch_rows([], rows=1)


def test_fetch_rows_fails_fast_when_page_returns_no_rows():
    class EmptyPageSource(HuggingFaceRowsSource):
        calls = 0

        def fetch_page(self, offset: int, length: int | None = None) -> list[dict]:
            type(self).calls += 1
            if type(self).calls == 1:
                return []
            raise AssertionError("fetch_rows should stop after an empty page")

    with pytest.raises(RuntimeError, match="No rows returned"):
        EmptyPageSource().fetch_rows([0], rows=1)
