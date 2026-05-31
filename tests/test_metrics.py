import pandas as pd

from src.metrics import (
    build_daily_kpis,
    build_funnel,
    build_retention,
    build_segments,
    build_top_paths,
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
                "price": 100.0,
                "user_id": 1,
                "user_session": "a",
            },
            {
                "event_time": pd.Timestamp("2019-11-01 09:05:00", tz="UTC"),
                "event_date": pd.to_datetime("2019-11-01").date(),
                "event_type": "cart",
                "product_id": 1,
                "category_code": "electronics.smartphone",
                "brand": "xiaomi",
                "price": 100.0,
                "user_id": 1,
                "user_session": "a",
            },
            {
                "event_time": pd.Timestamp("2019-11-01 09:08:00", tz="UTC"),
                "event_date": pd.to_datetime("2019-11-01").date(),
                "event_type": "purchase",
                "product_id": 1,
                "category_code": "electronics.smartphone",
                "brand": "xiaomi",
                "price": 100.0,
                "user_id": 1,
                "user_session": "a",
            },
            {
                "event_time": pd.Timestamp("2019-11-02 10:00:00", tz="UTC"),
                "event_date": pd.to_datetime("2019-11-02").date(),
                "event_type": "view",
                "product_id": 2,
                "category_code": "appliances.kitchen.washer",
                "brand": "lg",
                "price": 400.0,
                "user_id": 1,
                "user_session": "b",
            },
            {
                "event_time": pd.Timestamp("2019-11-01 11:00:00", tz="UTC"),
                "event_date": pd.to_datetime("2019-11-01").date(),
                "event_type": "view",
                "product_id": 3,
                "category_code": "electronics.audio",
                "brand": "sony",
                "price": 80.0,
                "user_id": 2,
                "user_session": "c",
            },
            {
                "event_time": pd.Timestamp("2019-11-01 11:05:00", tz="UTC"),
                "event_date": pd.to_datetime("2019-11-01").date(),
                "event_type": "cart",
                "product_id": 3,
                "category_code": "electronics.audio",
                "brand": "sony",
                "price": 80.0,
                "user_id": 2,
                "user_session": "c",
            },
            {
                "event_time": pd.Timestamp("2019-11-01 11:07:00", tz="UTC"),
                "event_date": pd.to_datetime("2019-11-01").date(),
                "event_type": "remove_from_cart",
                "product_id": 3,
                "category_code": "electronics.audio",
                "brand": "sony",
                "price": 80.0,
                "user_id": 2,
                "user_session": "c",
            },
        ]
    )


def test_build_daily_kpis_counts_users_sessions_events_and_gmv():
    kpis = build_daily_kpis(sample_events())

    first_day = kpis[kpis["event_date"] == pd.to_datetime("2019-11-01").date()].iloc[0]
    assert first_day["dau"] == 2
    assert first_day["sessions"] == 2
    assert first_day["views"] == 2
    assert first_day["cart_adds"] == 2
    assert first_day["purchases"] == 1
    assert first_day["gmv"] == 100.0


def test_build_funnel_reports_step_users_and_rates():
    funnel = build_funnel(sample_events())

    assert funnel["step"].tolist() == ["view", "cart", "purchase"]
    assert funnel["users"].tolist() == [2, 2, 1]
    assert funnel.loc[funnel["step"] == "purchase", "overall_rate"].iloc[0] == 0.5


def test_build_funnel_excludes_steps_without_earlier_steps():
    events = sample_events()
    # A user who carts and purchases but was never recorded viewing must not
    # inflate the cart/purchase steps above the view step.
    extra = pd.DataFrame(
        [
            {
                "event_time": pd.Timestamp("2019-11-03 09:00:00", tz="UTC"),
                "event_date": pd.to_datetime("2019-11-03").date(),
                "event_type": "cart",
                "product_id": 9,
                "category_code": "electronics.smartphone",
                "brand": "apple",
                "price": 900.0,
                "user_id": 99,
                "user_session": "z",
            },
            {
                "event_time": pd.Timestamp("2019-11-03 09:02:00", tz="UTC"),
                "event_date": pd.to_datetime("2019-11-03").date(),
                "event_type": "purchase",
                "product_id": 9,
                "category_code": "electronics.smartphone",
                "brand": "apple",
                "price": 900.0,
                "user_id": 99,
                "user_session": "z",
            },
        ]
    )
    funnel = build_funnel(pd.concat([events, extra], ignore_index=True))

    # view users stay {1, 2}; the no-view user 99 is excluded from cart/purchase.
    assert funnel["users"].tolist() == [2, 2, 1]
    # Every step rate is a real conversion fraction, never above 1.
    assert (funnel["step_rate"] <= 1.0).all()
    assert (funnel["overall_rate"] <= 1.0).all()


def test_build_retention_tracks_day_one_return():
    retention = build_retention(sample_events(), days=(0, 1, 7))

    cohort = retention[retention["cohort_date"] == pd.to_datetime("2019-11-01").date()]
    assert cohort.loc[cohort["days_since_first"] == 0, "retention_rate"].iloc[0] == 1.0
    assert cohort.loc[cohort["days_since_first"] == 1, "retention_rate"].iloc[0] == 0.5


def test_build_retention_default_excludes_trivial_day_zero():
    retention = build_retention(sample_events())

    assert set(retention["days_since_first"].unique()) == {1, 3, 7}


def test_build_top_paths_orders_events_inside_session():
    paths = build_top_paths(sample_events(), top_n=2)

    assert "view > cart > purchase" in paths["path"].tolist()
    assert "view > cart > remove_from_cart" in paths["path"].tolist()


def test_build_segments_assigns_behavior_based_segments():
    segments = build_segments(sample_events())

    labels = dict(zip(segments["segment"], segments["users"]))
    assert labels["Purchasers"] == 1
    assert labels["Cart Abandoners"] == 1
