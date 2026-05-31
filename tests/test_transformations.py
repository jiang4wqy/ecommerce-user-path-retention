import pandas as pd

from src.transform import add_time_features, clean_events


def test_clean_events_keeps_expected_events_and_required_fields():
    raw = pd.DataFrame(
        [
            {
                "event_time": "2019-11-01T00:00:00.000Z",
                "event_type": "view",
                "product_id": 1001,
                "category_code": "electronics.smartphone",
                "brand": "xiaomi",
                "price": 489.07,
                "user_id": 501,
                "user_session": "s1",
            },
            {
                "event_time": "2019-11-01T00:02:00.000Z",
                "event_type": "wishlist",
                "product_id": 1002,
                "category_code": "electronics.audio",
                "brand": "sony",
                "price": 99.99,
                "user_id": 501,
                "user_session": "s1",
            },
            {
                "event_time": "2019-11-01T00:04:00.000Z",
                "event_type": "purchase",
                "product_id": 1001,
                "category_code": "electronics.smartphone",
                "brand": "xiaomi",
                "price": 489.07,
                "user_id": None,
                "user_session": "s2",
            },
        ]
    )

    clean = clean_events(raw)

    assert clean["event_type"].tolist() == ["view"]
    assert set(clean.columns) >= {
        "event_time",
        "event_type",
        "user_id",
        "user_session",
        "product_id",
        "category_code",
        "brand",
        "price",
    }


def test_clean_events_clips_negative_prices_to_zero():
    raw = pd.DataFrame(
        [
            {
                "event_time": "2019-11-01T00:00:00.000Z",
                "event_type": "purchase",
                "product_id": 1001,
                "category_code": "electronics.smartphone",
                "brand": "xiaomi",
                "price": -12.5,
                "user_id": 501,
                "user_session": "s1",
            }
        ]
    )

    clean = clean_events(raw)

    assert clean.loc[0, "price"] == 0.0


def test_add_time_features_adds_date_hour_and_week():
    raw = pd.DataFrame(
        [
            {
                "event_time": "2019-11-03T13:25:00.000Z",
                "event_type": "cart",
                "product_id": 1001,
                "category_code": "electronics.smartphone",
                "brand": "xiaomi",
                "price": 489.07,
                "user_id": 501,
                "user_session": "s1",
            }
        ]
    )

    enriched = add_time_features(raw)

    assert str(enriched.loc[0, "event_date"]) == "2019-11-03"
    assert enriched.loc[0, "event_hour"] == 13
    assert str(enriched.loc[0, "week"]).startswith("2019-10-28")
