from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from src.config import PROJECT_ROOT, REPORTS_DIR


FORBIDDEN_DIRS = {"__pycache__", ".pytest_cache", ".streamlit"}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo", ".pyd", ".log"}
RAW_ALLOWED_FILES = {Path("README.md")}
REQUIRED_GITIGNORE_PATTERNS = {
    "__pycache__/",
    ".pytest_cache/",
    "*.pyc",
    "*.duckdb",
    "data/raw/*",
    "!data/raw/README.md",
}
IMAGE_LINK_RE = re.compile(r"!\[[^\]]*\]\((?!https?://)([^)#]+)(?:#[^)]*)?\)")


def audit_project(root: Path = PROJECT_ROOT) -> dict[str, Any]:
    root = Path(root).resolve()
    issues: list[str] = []
    checked_files = 0

    if not root.exists():
        return {"status": "fail", "root": str(root), "checked_files": 0, "issues": ["Project root does not exist"]}

    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if path.is_dir() and path.name in FORBIDDEN_DIRS:
            issues.append(f"Generated cache directory should be removed: {relative}")
        if path.is_file():
            checked_files += 1
            if path.suffix in FORBIDDEN_SUFFIXES:
                issues.append(f"Generated or local-only file should be removed: {relative}")

    _check_raw_data_dir(root, issues)
    _check_readme_assets(root, issues)
    _check_gitignore(root, issues)

    return {
        "status": "pass" if not issues else "fail",
        "root": str(root),
        "checked_files": checked_files,
        "issues": issues,
    }


def _check_raw_data_dir(root: Path, issues: list[str]) -> None:
    raw_dir = root / "data" / "raw"
    if not raw_dir.exists():
        return
    for path in raw_dir.rglob("*"):
        if path.is_file() and path.relative_to(raw_dir) not in RAW_ALLOWED_FILES:
            issues.append(f"Raw data file should not be included: {path.relative_to(root)}")


def _check_readme_assets(root: Path, issues: list[str]) -> None:
    readme = root / "README.md"
    if not readme.exists():
        issues.append("README.md is missing")
        return
    text = readme.read_text(encoding="utf-8")
    for match in IMAGE_LINK_RE.finditer(text):
        target = match.group(1).strip().replace("%20", " ")
        if target.startswith(("mailto:", "#")):
            continue
        target_path = (root / target).resolve()
        if root not in target_path.parents and target_path != root:
            issues.append(f"README image path escapes project root: {target}")
        elif not target_path.exists():
            issues.append(f"README image is missing: {target}")


def _check_gitignore(root: Path, issues: list[str]) -> None:
    gitignore = root / ".gitignore"
    if not gitignore.exists():
        issues.append(".gitignore is missing")
        return
    patterns = {
        line.strip()
        for line in gitignore.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.strip().startswith("#")
    }
    missing = sorted(REQUIRED_GITIGNORE_PATTERNS - patterns)
    if missing:
        issues.append(f".gitignore missing required patterns: {', '.join(missing)}")


def write_project_audit_report(root: Path = PROJECT_ROOT) -> Path:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    report = audit_project(root)
    output = REPORTS_DIR / "project_audit_report.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Check GitHub delivery hygiene for the project.")
    parser.add_argument("--root", type=Path, default=PROJECT_ROOT)
    args = parser.parse_args()
    report = audit_project(args.root)
    output = write_project_audit_report(args.root)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(f"Wrote project audit report: {output}")
    if report["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
