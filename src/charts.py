from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


FONT_FAMILY = "Microsoft YaHei, PingFang SC, Noto Sans CJK SC, Segoe UI, sans-serif"
CHART_COLORS = ["#0f766e", "#c47f22", "#b85c38", "#3f6f8f", "#8fa99d", "#6f5b3e"]
TREND_COLOR_MAP = {
    "dau": "#0f766e",
    "cart_adds": "#c47f22",
    "purchases": "#b85c38",
}
RETENTION_SCALE = [
    [0.0, "#f2f0e8"],
    [0.35, "#cdded6"],
    [0.7, "#64a89a"],
    [1.0, "#0f766e"],
]


def _style_figure(fig):
    fig.update_layout(
        font=dict(family=FONT_FAMILY, size=13, color="#1c302d"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=20, r=20, t=42, b=32),
        colorway=CHART_COLORS,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(
        showgrid=True,
        gridcolor="#ded8ca",
        zeroline=False,
        title_font_size=12,
        tickfont=dict(color="#33443f"),
    )
    fig.update_yaxes(
        showgrid=False,
        zeroline=False,
        title_font_size=12,
        tickfont=dict(color="#33443f"),
    )
    return fig


def kpi_cards(daily: pd.DataFrame) -> dict[str, str]:
    if daily.empty:
        return {"DAU均值": "0", "总GMV": "0", "平均购买转化率": "0.00%", "总购买事件": "0"}
    return {
        "DAU均值": f"{daily['dau'].mean():,.0f}",
        "总GMV": f"{daily['gmv'].sum():,.0f}",
        "平均购买转化率": f"{daily['purchase_rate'].mean():.2%}",
        "总购买事件": f"{daily['purchases'].sum():,.0f}",
    }


def trend_chart(daily: pd.DataFrame):
    chart_data = daily.melt(
        id_vars="event_date",
        value_vars=["dau", "cart_adds", "purchases"],
        var_name="metric",
        value_name="value",
    )
    return _style_figure(
        px.line(
            chart_data,
            x="event_date",
            y="value",
            color="metric",
            markers=True,
            color_discrete_map=TREND_COLOR_MAP,
        )
    )


def funnel_chart(funnel: pd.DataFrame):
    return _style_figure(go.Figure(
        go.Funnel(
            y=funnel["step"],
            x=funnel["users"],
            textinfo="value+percent initial",
        )
    ))


def retention_heatmap(retention: pd.DataFrame):
    matrix = retention.pivot(
        index="cohort_date", columns="days_since_first", values="retention_rate"
    )
    return _style_figure(px.imshow(
        matrix,
        labels={"x": "Days since first visit", "y": "Cohort date", "color": "Retention"},
        aspect="auto",
        color_continuous_scale=RETENTION_SCALE,
        text_auto=".1%",
    ))


def path_bar(paths: pd.DataFrame):
    return _style_figure(px.bar(
        paths.sort_values("sessions"),
        x="sessions",
        y="path",
        orientation="h",
        labels={"sessions": "Sessions", "path": "User path"},
    ))


def segment_chart(segments: pd.DataFrame):
    return _style_figure(
        px.pie(
            segments,
            names="segment",
            values="users",
            hole=0.45,
            color_discrete_sequence=CHART_COLORS,
        )
    )


def category_chart(category: pd.DataFrame):
    return _style_figure(px.bar(
        category.sort_values("gmv"),
        x="gmv",
        y="category_code",
        orientation="h",
        labels={"gmv": "GMV", "category_code": "Category"},
    ))


def price_band_chart(price_band: pd.DataFrame):
    return _style_figure(px.bar(
        price_band,
        x="price_band",
        y=["cart_rate", "purchase_rate"],
        barmode="group",
        labels={"value": "Rate", "price_band": "Price band", "variable": "Metric"},
    ))


def session_depth_chart(session_depth: pd.DataFrame):
    return _style_figure(px.bar(
        session_depth,
        x="session_type",
        y=["avg_events_per_session", "avg_products_per_session"],
        barmode="group",
        labels={"value": "Average", "session_type": "Session type", "variable": "Metric"},
    ))


def purchase_path_chart(purchase_paths: pd.DataFrame):
    chart_data = purchase_paths.copy()
    chart_data["label"] = chart_data["session_type"] + " | " + chart_data["path"]
    return _style_figure(px.bar(
        chart_data.sort_values("sessions"),
        x="sessions",
        y="label",
        orientation="h",
        labels={"sessions": "Sessions", "label": "Path"},
    ))
