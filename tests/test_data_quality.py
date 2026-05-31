import pandas as pd

from src.data_quality import validate_events


def test_validate_events_accepts_clean_event_sample():
    events = pd.DataFrame(
        [
            {
                "event_time": pd.Timestamp("2019-11-01 10:00:00", tz="UTC"),
                "event_type": "view",
                "product_id": 1,
                "category_code": "electronics.smartphone",
                "brand": "xiaomi",
                "price": 199.0,
                "user_id": 101,
                "user_session": "s1",
                "event_date": pd.to_datetime("2019-11-01").date(),
                "event_hour": 10,
                "week": pd.to_datetime("2019-10-28").date(),
            },
            {
                "event_time": pd.Timestamp("2019-11-01 10:05:00", tz="UTC"),
                "event_type": "purchase",
                "product_id": 1,
                "category_code": "electronics.smartphone",
                "brand": "xiaomi",
                "price": 199.0,
                "user_id": 101,
                "user_session": "s1",
                "event_date": pd.to_datetime("2019-11-01").date(),
                "event_hour": 10,
                "week": pd.to_datetime("2019-10-28").date(),
            },
        ]
    )

    report = validate_events(events)

    assert report["status"] == "pass"
    assert report["rows"] == 2
    assert report["event_types"]["purchase"] == 1
    assert report["issues"] == []


def test_validate_events_reports_missing_columns_and_invalid_events():
    events = pd.DataFrame(
        [
            {
                "event_time": pd.Timestamp("2019-11-01 10:00:00", tz="UTC"),
                "event_type": "wishlist",
                "price": -10.0,
                "user_id": 101,
                "user_session": None,
            }
        ]
    )

    report = validate_events(events)

    assert report["status"] == "fail"
    assert any("Missing required columns" in issue for issue in report["issues"])
    assert any("Invalid event_type values" in issue for issue in report["issues"])
    assert any("Negative prices" in issue for issue in report["issues"])
