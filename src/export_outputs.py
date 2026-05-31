from __future__ import annotations

from pathlib import Path

from src.analysis import build_all_outputs, load_events
from src.config import PROCESSED_DIR, REPORTS_DIR
from src.data_quality import write_quality_report
from src.insights import generate_insights


def main() -> None:
    events = load_events()
    outputs = build_all_outputs(events)
    metrics_dir = PROCESSED_DIR / "metrics"
    metrics_dir.mkdir(parents=True, exist_ok=True)
    for name, frame in outputs.items():
        frame.to_csv(metrics_dir / f"{name}.csv", index=False)

    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    insights_path = REPORTS_DIR / "insights.md"
    insights = generate_insights(outputs)
    insights_path.write_text(
        "# Key Insights\n\n" + "\n".join(f"- {line}" for line in insights) + "\n",
        encoding="utf-8",
    )
    quality_path = write_quality_report()
    print(f"Wrote metrics to {metrics_dir}")
    print(f"Wrote insights to {insights_path}")
    print(f"Wrote data quality report to {quality_path}")


if __name__ == "__main__":
    main()
