from pathlib import Path

from src.project_audit import audit_project


def test_audit_project_flags_generated_cache_directories(tmp_path):
    (tmp_path / ".gitignore").write_text(
        "__pycache__/\n.pytest_cache/\n*.pyc\n*.duckdb\ndata/raw/*\n!data/raw/README.md\n",
        encoding="utf-8",
    )
    (tmp_path / "README.md").write_text(
        "# Demo\n\n![Preview](assets/screenshots/dashboard_preview.png)\n",
        encoding="utf-8",
    )
    (tmp_path / "assets" / "screenshots").mkdir(parents=True)
    (tmp_path / "assets" / "screenshots" / "dashboard_preview.png").write_bytes(b"png")
    (tmp_path / "data" / "raw").mkdir(parents=True)
    (tmp_path / "data" / "raw" / "README.md").write_text("raw data ignored", encoding="utf-8")
    (tmp_path / "src" / "__pycache__").mkdir(parents=True)

    report = audit_project(tmp_path)

    assert report["status"] == "fail"
    assert any("__pycache__" in issue for issue in report["issues"])


def test_audit_project_accepts_clean_delivery_structure(tmp_path):
    (tmp_path / ".gitignore").write_text(
        "__pycache__/\n.pytest_cache/\n*.pyc\n*.duckdb\ndata/raw/*\n!data/raw/README.md\n",
        encoding="utf-8",
    )
    (tmp_path / "README.md").write_text(
        "# Demo\n\n![Preview](assets/screenshots/dashboard_preview.png)\n",
        encoding="utf-8",
    )
    (tmp_path / "assets" / "screenshots").mkdir(parents=True)
    (tmp_path / "assets" / "screenshots" / "dashboard_preview.png").write_bytes(b"png")
    (tmp_path / "data" / "raw").mkdir(parents=True)
    (tmp_path / "data" / "raw" / "README.md").write_text("raw data ignored", encoding="utf-8")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "analysis.py").write_text("print('ok')\n", encoding="utf-8")

    report = audit_project(Path(tmp_path))

    assert report["status"] == "pass"
    assert report["issues"] == []
