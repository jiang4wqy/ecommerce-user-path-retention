from __future__ import annotations

import json

import pandas as pd

from src.export_web_data import build_web_payload


def test_payload_sections_match_source_csv(tmp_path):
    metrics_dir = tmp_path / "metrics"
    metrics_dir.mkdir()
    funnel = pd.DataFrame(
        [{"step": "view", "users": 10, "sessions": 12, "overall_rate": 1.0, "step_rate": 1.0}]
    )
    funnel.to_csv(metrics_dir / "funnel.csv", index=False)
    quality = {"rows": 100, "users": 10, "sessions": 12,
               "date_range": {"min": "2019-11-01", "max": "2019-11-16"}}
    (tmp_path / "data_quality_report.json").write_text(json.dumps(quality), encoding="utf-8")
    (tmp_path / "insights.md").write_text("# Key Insights\n\n- 结论一\n- 结论二\n", encoding="utf-8")

    payload = build_web_payload(metrics_dir=metrics_dir,
                                quality_path=tmp_path / "data_quality_report.json",
                                insights_path=tmp_path / "insights.md")

    assert payload["funnel"] == funnel.to_dict("records")
    assert payload["scope"]["users"] == 10
    assert payload["scope"]["date_range"] == {"min": "2019-11-01", "max": "2019-11-16"}
    assert payload["insights"] == ["结论一", "结论二"]
