import pandas as pd

from src.metric_store import MetricStore
from src.transform import add_time_features


def test_metric_store_builds_core_tables_from_events(tmp_path):
    events = pd.DataFrame(
        [
            {
                "event_time": "2019-11-01T09:00:00.000Z",
                "event_type": "view",
                "product_id": 1,
                "category_code": "electronics.smartphone",
                "brand": "xiaomi",
                "price": 100.0,
                "user_id": 1,
                "user_session": "a",
            },
            {
                "event_time": "2019-11-01T09:05:00.000Z",
                "event_type": "cart",
                "product_id": 1,
                "category_code": "electronics.smartphone",
                "brand": "xiaomi",
                "price": 100.0,
                "user_id": 1,
                "user_session": "a",
            },
            {
                "event_time": "2019-11-01T09:08:00.000Z",
                "event_type": "purchase",
                "product_id": 1,
                "category_code": "electronics.smartphone",
                "brand": "xiaomi",
                "price": 100.0,
                "user_id": 1,
                "user_session": "a",
            },
        ]
    )
    path = tmp_path / "events.parquet"
    add_time_features(events).to_parquet(path, index=False)
    store = MetricStore(path)

    daily = store.table("daily_kpis")
    funnel = store.table("funnel")

    assert daily.loc[0, "purchases"] == 1
    assert funnel["step"].tolist() == ["view", "cart", "purchase"]
