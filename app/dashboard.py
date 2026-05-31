from __future__ import annotations

import sys
from html import escape
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.analysis import build_all_outputs, load_events
from src.charts import (
    category_chart,
    funnel_chart,
    kpi_cards,
    path_bar,
    price_band_chart,
    purchase_path_chart,
    retention_heatmap,
    segment_chart,
    session_depth_chart,
    trend_chart,
)
from src.data_quality import validate_events
from src.filters import EventFilters, filter_events
from src.insights import generate_insights


st.set_page_config(page_title="电商App用户路径与留存分析", layout="wide")

st.markdown(
    """
    <style>
    :root {
        --ink: #14231f;
        --muted: #51635d;
        --canvas: #f7f4ec;
        --canvas-soft: #f1f5f0;
        --surface: #fffdfa;
        --surface-2: #edf4f0;
        --border: #ded8ca;
        --teal: #0f766e;
        --teal-dark: #10413b;
        --sage: #8fa99d;
        --amber: #c47f22;
        --clay: #b85c38;
        --sidebar: #10201d;
        --sidebar-soft: #18332e;
        --sidebar-text: #eef6f1;
        --sidebar-muted: #b8cbc4;
    }
    html, body, .stApp {
        font-family: "Microsoft YaHei", "PingFang SC", "Noto Sans CJK SC", "Segoe UI", sans-serif;
        color: var(--ink) !important;
        background: var(--canvas) !important;
    }
    [data-testid="stAppViewContainer"] {
        background:
            radial-gradient(circle at top left, rgba(15, 118, 110, 0.08), transparent 32rem),
            linear-gradient(180deg, var(--canvas) 0%, var(--canvas-soft) 100%) !important;
    }
    [data-testid="stHeader"] {
        background: rgba(247, 244, 236, 0.86) !important;
        backdrop-filter: blur(8px);
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1320px;
    }
    h1 {
        font-size: 2.05rem !important;
        line-height: 1.22 !important;
        letter-spacing: 0 !important;
        font-weight: 760 !important;
        color: var(--ink) !important;
    }
    h2, h3 {
        letter-spacing: 0 !important;
        color: var(--teal-dark) !important;
    }
    [data-testid="stMarkdownContainer"] p {
        color: var(--muted);
    }
    [data-testid="stSidebar"] {
        background:
            linear-gradient(180deg, rgba(16, 32, 29, 0.98), rgba(19, 45, 40, 0.98)) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.10);
    }
    [data-testid="stSidebar"] h1 {
        font-size: 1.35rem !important;
        line-height: 1.25 !important;
        margin-bottom: 0.25rem;
        color: var(--sidebar-text) !important;
    }
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] li {
        font-size: 0.92rem !important;
        line-height: 1.52 !important;
        color: var(--sidebar-muted) !important;
    }
    [data-testid="stSidebar"] strong,
    [data-testid="stSidebar"] h3 {
        color: var(--sidebar-text) !important;
    }
    [data-testid="stMetric"] {
        background: var(--surface);
        border: 1px solid var(--border);
        border-left: 4px solid var(--teal);
        border-radius: 8px;
        padding: 15px 17px;
        box-shadow: 0 12px 28px rgba(20, 35, 31, 0.07);
    }
    [data-testid="stMetricLabel"] {
        color: var(--muted);
        font-weight: 650;
    }
    [data-testid="stMetricValue"] {
        color: var(--teal-dark);
        font-weight: 760;
    }
    [data-testid="stSidebar"] [data-testid="stMetric"] {
        background: rgba(255, 255, 255, 0.08);
        border-color: rgba(255, 255, 255, 0.14);
        border-left-color: var(--sage);
        box-shadow: none;
    }
    [data-testid="stSidebar"] [data-testid="stMetricLabel"] {
        color: var(--sidebar-muted);
    }
    [data-testid="stSidebar"] [data-testid="stMetricValue"] {
        color: var(--sidebar-text);
    }
    div[data-testid="stInfo"] {
        background: #e7f1ed;
        border: 1px solid #c7ddd5;
        border-left: 5px solid var(--teal);
        color: var(--teal-dark);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        border-bottom: 1px solid var(--border);
    }
    .stTabs [data-baseweb="tab"] {
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 8px 14px;
        background: rgba(255, 253, 250, 0.92);
        color: var(--muted) !important;
    }
    .stTabs [data-baseweb="tab"] p {
        color: var(--muted) !important;
        font-weight: 650;
    }
    .stTabs [aria-selected="true"] {
        background: var(--teal-dark) !important;
        border-color: var(--teal-dark) !important;
        box-shadow: 0 8px 18px rgba(15, 65, 59, 0.18);
    }
    .stTabs [aria-selected="true"] p {
        color: #ffffff !important;
    }
    .sidebar-panel {
        background: rgba(255, 255, 255, 0.075);
        border: 1px solid rgba(255, 255, 255, 0.13);
        border-radius: 8px;
        padding: 12px 13px;
        margin: 12px 0;
    }
    .sidebar-panel-title {
        color: var(--sidebar-text);
        font-size: 0.88rem;
        font-weight: 760;
        margin-bottom: 6px;
    }
    .sidebar-flow {
        margin: 0;
        padding-left: 18px;
    }
    .sidebar-flow li {
        margin: 5px 0;
    }
    .scope-note {
        color: var(--sidebar-muted);
        font-size: 0.82rem;
        line-height: 1.45;
        margin-top: 8px;
    }
    div[data-testid="stExpander"] {
        background: rgba(255, 253, 250, 0.72);
        border: 1px solid var(--border);
        border-radius: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_data(show_spinner=False)
def load_raw_events():
    return load_events()


@st.cache_data(show_spinner=False)
def compute_outputs(events):
    # Cached on the filtered frame's contents so repeated/identical filter
    # selections don't re-run every groupby, pivot and path join.
    return build_all_outputs(events)


def render_sidebar_intro(events):
    st.sidebar.title("分析工作台")
    st.sidebar.caption("用公开电商行为日志复现产品数据分析：先定义口径，再看转化、留存、路径和分层。")
    st.sidebar.markdown(
        """
        <div class="sidebar-panel">
          <div class="sidebar-panel-title">分析链路</div>
          <ol class="sidebar-flow">
            <li><strong>Overview：先看整体是否健康</strong><br>DAU、Session、购买数、GMV 是否同步变化。</li>
            <li><strong>Conversion：定位哪里流失</strong><br>拆 view → cart → purchase，判断问题在兴趣、加购还是支付前。</li>
            <li><strong>Retention：看用户是否回来</strong><br>按首次访问日观察 D1/D3/D7 复访。</li>
            <li><strong>User Path：看真实行为顺序</strong><br>比较购买 session 与未购买 session 的路径差异。</li>
            <li><strong>Segments：找到可运营人群</strong><br>区分浏览型、加购未买型、购买型和复购型用户。</li>
            <li><strong>Insights：沉淀业务结论</strong><br>把指标异常翻译成产品和运营建议。</li>
          </ol>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.markdown(
        f"""
        <div class="sidebar-panel">
          <div class="sidebar-panel-title">原始样本口径</div>
          <div>公开匿名化电商事件日志，核心字段包括 event_type、user_id、user_session、price、category_code。</div>
          <div class="scope-note">当前样本：{len(events):,} 条事件，{events["user_id"].nunique():,} 个用户，
          覆盖 {events["event_date"].min()} 至 {events["event_date"].max()}。</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_current_scope(filtered_events):
    st.sidebar.markdown("### 当前筛选结果")
    col_a, col_b = st.sidebar.columns(2)
    col_a.metric("筛选后事件", f"{len(filtered_events):,}")
    col_b.metric("用户数", f"{filtered_events['user_id'].nunique():,}")
    st.sidebar.metric("Session 数", f"{filtered_events['user_session'].nunique():,}")
    if filtered_events.empty:
        st.sidebar.caption("当前筛选没有命中事件，请放宽筛选条件。")
        return
    event_counts = filtered_events["event_type"].value_counts().to_dict()
    summary = " / ".join(
        f"{escape(event_type)} {count:,}"
        for event_type, count in event_counts.items()
    )
    st.sidebar.markdown(
        f"""
        <div class="scope-note">
        事件构成：{summary}<br>
        日期范围：{filtered_events["event_date"].min()} - {filtered_events["event_date"].max()}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _top_options(series, limit=60):
    """Most frequent values (excluding 'unknown'), plus the full distinct count."""
    counts = series[series != "unknown"].dropna().value_counts()
    return counts.index[:limit].tolist(), int(counts.size)


def apply_filters(events):
    render_sidebar_intro(events)
    st.sidebar.markdown("### 筛选口径")
    st.sidebar.caption("筛选后，所有图表会同步刷新，用来回答某个品类、品牌或价格段表现如何。")
    min_date = events["event_date"].min()
    max_date = events["event_date"].max()
    selected_dates = st.sidebar.date_input(
        "事件日期范围",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
    start_date = None
    end_date = None
    if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
        start_date, end_date = selected_dates

    category_options, category_total = _top_options(events["category_code"])
    selected_categories = st.sidebar.multiselect("品类", category_options, default=[])
    if category_total > len(category_options):
        st.sidebar.caption(f"按出现频次列出 Top {len(category_options)}/{category_total} 个品类")

    brand_options, brand_total = _top_options(events["brand"])
    selected_brands = st.sidebar.multiselect("品牌", brand_options, default=[])
    if brand_total > len(brand_options):
        st.sidebar.caption(f"按出现频次列出 Top {len(brand_options)}/{brand_total} 个品牌")

    max_price = float(events["price"].max()) if not events.empty else 0.0
    selected_price = st.sidebar.slider("价格上限", 0.0, max(max_price, 1.0), max(max_price, 1.0))
    filtered = filter_events(
        events,
        EventFilters(
            start_date=start_date,
            end_date=end_date,
            categories=tuple(selected_categories),
            brands=tuple(selected_brands),
            max_price=selected_price,
        ),
    )
    render_current_scope(filtered)
    return filtered


events_df = load_raw_events()
filtered_events = apply_filters(events_df)

st.title("电商 App 用户行为路径与转化留存分析")
st.caption("Public anonymized ecommerce event logs | SQL + Python + Streamlit + Plotly")
st.markdown(
    "这份 dashboard 按真实产品分析顺序组织：先看整体经营状态，再定位转化流失，随后验证留存、路径和用户分层，最后输出业务建议。"
)

if filtered_events.empty:
    st.warning("当前筛选条件下没有数据，请放宽日期、品类、品牌或价格范围。")
    st.stop()

outputs = compute_outputs(filtered_events)
daily = outputs["daily_kpis"]
funnel = outputs["funnel"]
retention = outputs["retention"]
paths = outputs["paths"]
segments = outputs["segments"]
category = outputs["category"]
price_band = outputs["price_band"]
session_depth = outputs["session_depth"]
purchase_paths = outputs["purchase_paths"]
cart_abandonment = outputs["cart_abandonment"]
insights = generate_insights(outputs)
quality = validate_events(filtered_events)

tabs = st.tabs(["Overview", "Conversion", "Retention", "User Path", "Segments", "Insights"])

with tabs[0]:
    st.subheader("核心经营与行为指标")
    cards = kpi_cards(daily)
    cols = st.columns(len(cards))
    for col, (label, value) in zip(cols, cards.items()):
        col.metric(label, value)
    st.plotly_chart(trend_chart(daily), width="stretch")
    st.info("这页用于快速判断样本期内活跃、加购和购买是否同步变化。")
    with st.expander("数据质量与字段口径"):
        st.json(quality)
        st.dataframe(filtered_events.head(80), width="stretch")

with tabs[1]:
    st.subheader("转化漏斗与价格带表现")
    left, right = st.columns([1, 1])
    with left:
        st.plotly_chart(funnel_chart(funnel), width="stretch")
        st.write("漏斗展示用户从浏览到加购、再到购买的主要流失环节。")
    with right:
        st.plotly_chart(price_band_chart(price_band), width="stretch")
        st.write("价格带分析用于判断不同客单价区间的加购率和购买转化率。")
    st.dataframe(cart_abandonment, width="stretch")
    st.write("加购未买用户是最直接的运营触达对象，可用于购物车召回和价格提醒策略。")

with tabs[2]:
    st.subheader("Cohort 留存")
    st.plotly_chart(retention_heatmap(retention), width="stretch")
    st.write("留存热力图用于观察新用户首访后 D1/D3/D7 的复访表现。")

with tabs[3]:
    st.subheader("用户路径与 session 深度")
    st.plotly_chart(path_bar(paths), width="stretch")
    st.write("Top 路径帮助判断大多数 session 是否停留在浏览阶段。")
    st.plotly_chart(purchase_path_chart(purchase_paths), width="stretch")
    st.write("购买路径对比展示购买 session 和未购买 session 的行为差异。")

with tabs[4]:
    st.subheader("用户分层、品类与访问深度")
    col_a, col_b = st.columns([1, 1])
    with col_a:
        st.plotly_chart(segment_chart(segments), width="stretch")
        st.dataframe(segments, width="stretch")
    with col_b:
        st.plotly_chart(session_depth_chart(session_depth), width="stretch")
        st.dataframe(session_depth, width="stretch")
    st.plotly_chart(category_chart(category), width="stretch")
    st.write("分层、访问深度和品类表现共同支持差异化推荐、召回和活动资源分配。")

with tabs[5]:
    st.subheader("业务洞察与优化建议")
    for item in insights:
        st.markdown(f"- {item}")
    st.markdown(
        "这个项目重点展示从行为日志到指标体系、产品诊断和运营动作的完整分析链路。"
    )
