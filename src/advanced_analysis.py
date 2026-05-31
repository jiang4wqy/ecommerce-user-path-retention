from __future__ import annotations

import pandas as pd

from src.metrics import _safe_divide, purchase_revenue


PRICE_BINS = [0, 100, 300, 500, 1000, float("inf")]
PRICE_LABELS = ["0-100", "100-300", "300-500", "500-1000", "1000+"]


def build_price_band_analysis(events: pd.DataFrame) -> pd.DataFrame:
    data = events.copy()
    data["price_band"] = pd.cut(
        data["price"], bins=PRICE_BINS, labels=PRICE_LABELS, right=True, include_lowest=True
    )
    data["_gmv"] = purchase_revenue(data)
    result = (
        data.groupby("price_band", observed=False)
        .agg(
            users=("user_id", "nunique"),
            views=("event_type", lambda s: (s == "view").sum()),
            carts=("event_type", lambda s: (s == "cart").sum()),
            purchases=("event_type", lambda s: (s == "purchase").sum()),
            gmv=("_gmv", "sum"),
        )
        .reset_index()
    )
    result["cart_rate"] = _safe_divide(result["carts"], result["views"])
    result["purchase_rate"] = _safe_divide(result["purchases"], result["views"])
    return result


def build_session_depth(events: pd.DataFrame) -> pd.DataFrame:
    sessions = (
        events.groupby("user_session")
        .agg(
            events=("event_type", "size"),
            unique_products=("product_id", "nunique"),
            purchased=("event_type", lambda s: (s == "purchase").any()),
        )
        .reset_index()
    )
    sessions["session_type"] = sessions["purchased"].map(
        {True: "Purchased", False: "No Purchase"}
    )
    return (
        sessions.groupby("session_type")
        .agg(
            sessions=("user_session", "nunique"),
            avg_events_per_session=("events", "mean"),
            avg_products_per_session=("unique_products", "mean"),
        )
        .reset_index()
        .round(2)
    )


def build_cart_abandonment(events: pd.DataFrame) -> pd.DataFrame:
    user_flags = events.pivot_table(
        index="user_id",
        columns="event_type",
        values="user_session",
        aggfunc="count",
        fill_value=0,
    )
    for column in ["cart", "purchase"]:
        if column not in user_flags:
            user_flags[column] = 0
    cart_users = int((user_flags["cart"] > 0).sum())
    purchase_after_cart = int(((user_flags["cart"] > 0) & (user_flags["purchase"] > 0)).sum())
    cart_without_purchase = int(((user_flags["cart"] > 0) & (user_flags["purchase"] == 0)).sum())
    abandonment_rate = cart_without_purchase / cart_users if cart_users else 0.0
    return pd.DataFrame(
        [
            {
                "cart_users": cart_users,
                "cart_purchase_users": purchase_after_cart,
                "cart_without_purchase_users": cart_without_purchase,
                "abandonment_rate": round(abandonment_rate, 4),
            }
        ]
    )


def build_purchase_path_comparison(
    events: pd.DataFrame, top_n: int = 8, max_path_len: int = 5
) -> pd.DataFrame:
    ordered = events.sort_values(["user_session", "event_time"])
    session_flags = (
        ordered.groupby("user_session")["event_type"]
        .apply(lambda s: "Purchased" if (s == "purchase").any() else "No Purchase")
        .reset_index(name="session_type")
    )
    paths = (
        ordered.groupby("user_session")["event_type"]
        .apply(lambda s: " > ".join(s.head(max_path_len)))
        .reset_index(name="path")
        .merge(session_flags, on="user_session", how="left")
    )
    return (
        paths.groupby(["session_type", "path"])["user_session"]
        .nunique()
        .reset_index(name="sessions")
        .sort_values(["session_type", "sessions"], ascending=[True, False])
        .groupby("session_type")
        .head(top_n)
        .reset_index(drop=True)
    )
