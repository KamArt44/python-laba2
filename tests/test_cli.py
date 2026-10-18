import json
import os
import subprocess
import sys
from pathlib import Path

import pytest


def run_cli(tmp_path, *arguments):
    env = os.environ.copy()
    source = str(Path(__file__).resolve().parents[1] / "src")
    env["PYTHONPATH"] = source + os.pathsep + env.get("PYTHONPATH", "")
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(
        [sys.executable, "-m", "streamstats", *arguments],
        cwd=tmp_path,
        env=env,
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=False,
    )


def test_cli_report(tmp_path):
    path = tmp_path / "events.jsonl"
    path.write_text(
        '{"timestamp":"2026-10-13T10:00:00Z","level":"ERROR",'
        '"source":"серверр","message":"Ошибка"}\n',
        "utf-8",
    )
    result = run_cli(
        tmp_path,
        "analyze",
        "events.jsonl",
        "--format",
        "jsonl",
        "--output",
        "report.json",
    )
    assert result.returncode == 0
    text = (tmp_path / "report.json").read_text("utf-8")
    assert "серверр" in text
    assert json.loads(text)["total_events"] == 1


@pytest.mark.parametrize("format_name", ["csv", "jsonl"])
def test_cli_invalid_modes(tmp_path, format_name):
    path = tmp_path / f"invalid.{format_name}"
    content = (
        "{}\n"
        if format_name == "jsonl"
        else ("timestamp,level,source,message\nнет,INFO,api,ошибка\n")
    )
    path.write_text(content, "utf-8")
    args = ("analyze", path.name, "--format", format_name)
    result = run_cli(tmp_path, *args)
    assert result.returncode == 2
    assert "Файл №1" in result.stderr
    assert "строка" in result.stderr
    assert "Traceback" not in result.stderr
    result = run_cli(tmp_path, *args, "--skip-invalid")
    assert result.returncode == 0
    assert "WARNING" in result.stderr
    assert json.loads(result.stdout)["skipped_lines"] == 1

