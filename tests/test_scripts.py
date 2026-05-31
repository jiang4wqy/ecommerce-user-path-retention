from pathlib import Path


def test_pipeline_script_checks_native_command_exit_codes():
    script = Path("run_pipeline.ps1").read_text(encoding="utf-8")

    assert "$LASTEXITCODE" in script
    assert "Invoke-PythonModule" in script


def test_pipeline_script_can_run_without_network_by_default():
    script = Path("run_pipeline.ps1").read_text(encoding="utf-8")

    assert "RefreshData" in script
    assert "events_sample.csv" in script
