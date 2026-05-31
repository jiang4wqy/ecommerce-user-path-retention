from streamlit.testing.v1 import AppTest


def test_dashboard_renders_core_sections_without_exception():
    app = AppTest.from_file("app/dashboard.py")
    app.run(timeout=30)

    assert not app.exception
    assert app.title[0].value == "电商 App 用户行为路径与转化留存分析"
    assert [tab.label for tab in app.tabs] == [
        "Overview",
        "Conversion",
        "Retention",
        "User Path",
        "Segments",
        "Insights",
    ]


def test_dashboard_sidebar_explains_analysis_flow_and_current_scope():
    app = AppTest.from_file("app/dashboard.py")
    app.run(timeout=30)

    sidebar_text = "\n".join(markdown.value for markdown in app.sidebar.markdown)
    metric_labels = [metric.label for metric in app.sidebar.metric]

    assert app.sidebar.title[0].value == "分析工作台"
    assert "分析链路" in sidebar_text
    assert "Overview：先看整体是否健康" in sidebar_text
    assert "筛选口径" in sidebar_text
    assert {"筛选后事件", "用户数", "Session 数"} <= set(metric_labels)
