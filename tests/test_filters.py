import pandas as pd

from src.filters import EventFilters, filter_events


def sample_events():
    return pd.DataFrame(
        [
            {
                "event_date": pd.to_datetime("2019-11-01").date(),
                "category_code": "electronics.smartphone",
                "brand": "xiaomi",
                "price": 199.0,
                "event_type": "view",
            },
            {
                "event_date": pd.to_datetime("2019-11-02").date(),
                "category_code": "electronics.audio",
                "brand": "sony",
                "price": 79.0,
                "event_type": "cart",
            },
            {
                "event_date": pd.to_datetime("2019-11-03").date(),
                "category_code": "appliances.kitchen",
                "brand": "lg",
                "price": 520.0,
                "event_type": "purchase",
            },
        ]
    )


def test_filter_events_applies_date_category_brand_and_price():
    filters = EventFilters(
        start_date=pd.to_datetime("2019-11-01").date(),
        end_date=pd.to_datetime("2019-11-02").date(),
        categories=("electronics.audio",),
        brands=("sony",),
        max_price=100.0,
    )

    result = filter_events(sample_events(), filters)

    assert len(result) == 1
    assert result.loc[0, "brand"] == "sony"
    assert result.loc[0, "event_type"] == "cart"


def test_filter_events_returns_empty_frame_with_original_columns():
    filters = EventFilters(categories=("not.present",))

    result = filter_events(sample_events(), filters)

    assert result.empty
    assert result.columns.tolist() == sample_events().columns.tolist()
