from __future__ import annotations

import pandas as pd


def build_daily_kpis(events: pd.DataFrame) -> pd.DataFrame:
    data = events.assign(_gmv=purchase_revenue(events))
    daily = (
        data.groupby("event_date")
        .agg(
            dau=("user_id", "nunique"),
            sessions=("user_session", "nunique"),
            events=("event_type", "size"),
            views=("event_type", lambda s: (s == "view").sum()),
            cart_adds=("event_type", lambda s: (s == "cart").sum()),
            cart_removes=("event_type", lambda s: (s == "remove_from_cart").sum()),
            purchases=("event_type", lambda s: (s == "purchase").sum()),
            gmv=("_gmv", "sum"),
        )
        .reset_index()
        .sort_values("event_date")
    )
    daily["cart_rate"] = _safe_divide(daily["cart_adds"], daily["views"])
    daily["purchase_rate"] = _safe_divide(daily["purchases"], daily["views"])
    daily["avg_order_value"] = _safe_divide(daily["gmv"], daily["purchases"])
    return daily


def build_funnel(events: pd.DataFrame) -> pd.DataFrame:
    steps = ["view", "cart", "purchase"]
    users_by_step = {
        step: set(events.loc[events["event_type"] == step, "user_id"]) for step in steps
    }
    sessions_by_step = {
        step: set(events.loc[events["event_type"] == step, "user_session"]) for step in steps
    }

    rows = []
    cum_users: set | None = None
    cum_sessions: set | None = None
    top = None
    previous_users = None
    for step in steps:
        # Cumulative intersection enforces a true funnel: a user counts at a step
        # only if they also completed every earlier step (view ⊇ cart ⊇ purchase).
        cum_users = users_by_step[step] if cum_users is None else cum_users & users_by_step[step]
        cum_sessions = (
            sessions_by_step[step] if cum_sessions is None else cum_sessions & sessions_by_step[step]
        )
        user_count = len(cum_users)
        if top is None:
            top = user_count
        rows.append(
            {
                "step": step,
                "users": int(user_count),
                "sessions": int(len(cum_sessions)),
                "overall_rate": round(user_count / top, 4) if top else 0.0,
                "step_rate": round(user_count / previous_users, 4)
                if previous_users
                else 1.0,
            }
        )
        previous_users = user_count
    return pd.DataFrame(rows)


def build_retention(events: pd.DataFrame, days: tuple[int, ...] = (1, 3, 7)) -> pd.DataFrame:
    # Day 0 is the cohort itself and is always 100% by construction, so it is
    # excluded from the default; pass days explicitly to include it.
    user_dates = events[["user_id", "event_date"]].drop_duplicates().copy()
    first_seen = user_dates.groupby("user_id", as_index=False)["event_date"].min()
    first_seen = first_seen.rename(columns={"event_date": "cohort_date"})
    retained = user_dates.merge(first_seen, on="user_id", how="left")
    retained["days_since_first"] = (
        pd.to_datetime(retained["event_date"]) - pd.to_datetime(retained["cohort_date"])
    ).dt.days
    retained = retained[retained["days_since_first"].isin(days)]

    counts = (
        retained.groupby(["cohort_date", "days_since_first"])["user_id"]
        .nunique()
        .reset_index(name="retained_users")
    )
    cohort_sizes = first_seen.groupby("cohort_date")["user_id"].nunique().reset_index()
    cohort_sizes = cohort_sizes.rename(columns={"user_id": "cohort_size"})

    cohorts = sorted(first_seen["cohort_date"].unique())
    grid = pd.MultiIndex.from_product(
        [cohorts, days], names=["cohort_date", "days_since_first"]
    ).to_frame(index=False)
    retention = (
        grid.merge(counts, on=["cohort_date", "days_since_first"], how="left")
        .merge(cohort_sizes, on="cohort_date", how="left")
        .fillna({"retained_users": 0})
    )
    retention["retained_users"] = retention["retained_users"].astype(int)
    retention["retention_rate"] = _safe_divide(
        retention["retained_users"], retention["cohort_size"]
    )
    return retention.sort_values(["cohort_date", "days_since_first"]).reset_index(drop=True)


def build_top_paths(
    events: pd.DataFrame, top_n: int = 10, max_path_len: int = 5
) -> pd.DataFrame:
    ordered = events.sort_values(["user_session", "event_time"]).copy()
    paths = (
        ordered.groupby("user_session")["event_type"]
        .apply(lambda s: " > ".join(s.head(max_path_len)))
        .reset_index(name="path")
    )
    paths = (
        paths.groupby("path")["user_session"]
        .nunique()
        .reset_index(name="sessions")
    )
    paths["path_length"] = paths["path"].str.count(">") + 1
    paths = (
        paths.sort_values(["sessions", "path_length", "path"], ascending=[False, False, True])
        .head(top_n)
        .drop(columns=["path_length"])
        .reset_index(drop=True)
    )
    return paths


def build_segments(events: pd.DataFrame) -> pd.DataFrame:
    user_behavior = events.pivot_table(
        index="user_id",
        columns="event_type",
        values="user_session",
        aggfunc="count",
        fill_value=0,
    ).reset_index()
    for column in ["view", "cart", "remove_from_cart", "purchase"]:
        if column not in user_behavior:
            user_behavior[column] = 0

    def classify(row: pd.Series) -> str:
        if row["purchase"] >= 2:
            return "Repeat Purchasers"
        if row["purchase"] >= 1:
            return "Purchasers"
        if row["cart"] >= 1:
            return "Cart Abandoners"
        return "Browsers Only"

    user_behavior["segment"] = user_behavior.apply(classify, axis=1)
    segment_sizes = (
        user_behavior.groupby("segment")["user_id"]
        .nunique()
        .reset_index(name="users")
        .sort_values("users", ascending=False)
    )
    total_users = segment_sizes["users"].sum()
    segment_sizes["share"] = _safe_divide(segment_sizes["users"], total_users)
    return segment_sizes.reset_index(drop=True)


def purchase_revenue(events: pd.DataFrame) -> pd.Series:
    """Per-row GMV contribution: price on purchase rows, 0 otherwise."""
    return events["price"].where(events["event_type"] == "purchase", 0.0)


def _safe_divide(numerator: pd.Series, denominator) -> pd.Series:
    """Divide a Series by a Series or scalar, mapping inf/NaN to 0 and rounding."""
    return (numerator / denominator).replace([float("inf"), float("-inf")], 0).fillna(0).round(4)
