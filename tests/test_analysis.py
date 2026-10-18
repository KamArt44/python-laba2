import json

import pytest

from streamstats.analysis import analyze


def write_events(path, rows):
    with path.open("w", encoding="utf-8") as file:
        for timestamp, level, source in rows:
            data = {
                "timestamp": timestamp,
                "level": level,
                "source": source,
                "message": "Сообщение 🐍",
            }
            file.write(json.dumps(data, ensure_ascii=False) + "\n")

def test_multiple_files_and_unicode(tmp_path):
    first = tmp_path / "first.jsonl"
    second = tmp_path / "second.jsonl"
    write_events(
        first,
        [
            ("2026-10-13T12:00:00Z", "ERROR", "база данных"),
            ("2026-10-13T10:00:00Z", "INFO", "api"),
        ],
    )
    write_events(
        second,
        [
            ("2026-10-13T14:00:00+03:00", "CRITICAL", "база данных"),
            ("2026-10-13T09:00:00", "ERROR", "api"),
        ],
    )
    result = analyze([str(first), str(second)], "jsonl")
    assert result["total_events"] == 4
    assert result["levels"] == {
        "DEBUG": 0,
        "INFO": 1,
        "WARNING": 0,
        "ERROR": 2,
        "CRITICAL": 1,
    }
    assert result["sources"] == {"база данных": 2, "api": 2}
    assert result["top_error_sources"] == [
        {"source": "база данных", "count": 2},
        {"source": "api", "count": 1},
    ]
    assert result["first_timestamp"] == "2026-10-13T09:00:00+00:00"
    assert result["last_timestamp"] == "2026-10-13T12:00:00+00:00"


def test_top_five(tmp_path):
    path = tmp_path / "events.jsonl"
    rows = []
    for index in range(7):
        for _ in range(index + 1):
            rows.append(("2026-10-13T10:00:00Z", "ERROR", f"source-{index}"))
    write_events(path, rows)
    top = analyze([str(path)], "jsonl")["top_error_sources"]
    assert [item["count"] for item in top] == [7, 6, 5, 4, 3]


@pytest.mark.parametrize("format_name", ["csv", "jsonl"])
def test_skipped_count(tmp_path, format_name):
    path = tmp_path / "invalid"
    if format_name == "jsonl":
        path.write_text("не JSON\n{}\n", "utf-8")
    else:
        path.write_text("timestamp,level,source,message\nнет,INFO,api,x\n", "utf-8")
    result = analyze([str(path)], format_name, skip_invalid=True)
    assert result["skipped_lines"] == (2 if format_name == "jsonl" else 1)
    assert result["total_events"] == 0


