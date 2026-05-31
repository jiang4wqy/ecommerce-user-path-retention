import pandas as pd

from src.advanced_analysis import (
    build_cart_abandonment,
    build_price_band_analysis,
    build_purchase_path_comparison,
    build_session_depth,
)


def sample_events():
    return pd.DataFrame(
        [
            {
                "event_time": pd.Timestamp("2019-11-01 09:00:00", tz="UTC"),
                "event_date": pd.to_datetime("2019-11-01").date(),
                "event_type": "view",
                "product_id": 1,
                "category_code": "electronics.smartphone",
                "brand": "xiaomi",
                "price": 99.0,
                "user_id": 1,
                "user_session": "a",
            },
            {
                "event_time": pd.Timestamp("2019-11-01 09:01:00", tz="UTC"),
                "event_date": pd.to_datetime("2019-11-01").date(),
                "event_type": "cart",
                "product_id": 1,
                "category_code": "electronics.smartphone",
                "brand": "xiaomi",
                "price": 99.0,
                "user_id": 1,
                "user_session": "a",
            },
            {
                "event_time": pd.Timestamp("2019-11-01 09:02:00", tz="UTC"),
                "event_date": pd.to_datetime("2019-11-01").date(),
                "event_type": "purchase",
                "product_id": 1,
                "category_code": "electronics.smartphone",
                "brand": "xiaomi",
                "price": 99.0,
                "user_id": 1,
                "user_session": "a",
            },
            {
                "event_time": pd.Timestamp("2019-11-01 10:00:00", tz="UTC"),
                "event_date": pd.to_datetime("2019-11-01").date(),
                "event_type": "view",
                "product_id": 2,
                "category_code": "electronics.audio",
                "brand": "sony",
                "price": 499.0,
                "user_id": 2,
                "user_session": "b",
            },
            {
                "event_time": pd.Timestamp("2019-11-01 10:03:00", tz="UTC"),
                "event_date": pd.to_datetime("2019-11-01").date(),
                "event_type": "cart",
                "product_id": 2,
                "category_code": "electronics.audio",
                "brand": "sony",
                "price": 499.0,
                "user_id": 2,
                "user_session": "b",
            },
        ]
    )


def test_build_price_band_analysis_groups_conversion_metrics():
    result = build_price_band_analysis(sample_events())

    assert set(result["price_band"]) >= {"0-100", "300-500"}
    assert result.loc[result["price_band"] == "0-100", "purchases"].iloc[0] == 1


def test_build_session_depth_tracks_purchase_sessions():
    result = build_session_depth(sample_events())

    purchased = result[result["session_type"] == "Purchased"].iloc[0]
    abandoned = result[result["session_type"] == "No Purchase"].iloc[0]
    assert purchased["avg_events_per_session"] == 3
    assert abandoned["avg_events_per_session"] == 2


def test_build_cart_abandonment_counts_cart_without_purchase_users():
    result = build_cart_abandonment(sample_events())

    assert result.loc[0, "cart_users"] == 2
    assert result.loc[0, "cart_without_purchase_users"] == 1


def test_build_purchase_path_comparison_splits_purchase_and_non_purchase_paths():
    result = build_purchase_path_comparison(sample_events())

    assert set(result["session_type"]) == {"Purchased", "No Purchase"}
    assert "view > cart > purchase" in result["path"].tolist()
