import pytest

from streamstats.parsers import read_csv, read_jsonl

JSON_LINE = (
    '{"timestamp":"2026-10-13T10:00:00Z","level":"INFO",'
    '"source":"api","message":"Привет, мир"}\n'
)
CSV_HEADER = "timestamp,level,source,message\n"
CSV_LINE = '2026-10-13T10:00:00Z,INFO,api,"Привет, мир"\n'


def test_jsonl_parser(tmp_path):
    path = tmp_path / "events.jsonl"
    path.write_text(JSON_LINE, encoding="utf-8")
    events = list(read_jsonl(path))
    assert len(events) == 1
    assert events[0]["message"] == "Привет, мир"


def test_csv_parser(tmp_path):
    path = tmp_path / "events.csv"
    path.write_text(CSV_HEADER + CSV_LINE, encoding="utf-8")
    events = list(read_csv(path))
    assert len(events) == 1
    assert events[0]["message"] == "Привет, мир"


@pytest.mark.parametrize("reader", [read_csv, read_jsonl])
def test_empty_file(tmp_path, reader):
    path = tmp_path / "empty"
    path.write_text("", encoding="utf-8")
    assert list(reader(path)) == []
