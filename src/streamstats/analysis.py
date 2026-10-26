

from streamstats.models import LEVELS, parse_timestamp
from streamstats.parsers import read_files


def analyze_events(events):
    total = 0
    skipped_lines = 0
    level_counts = {}
    source_counts = {}
    error_counts = {}

    for level in LEVELS:
        level_counts[level] = 0

    first = None
    last = None

    for event in events:
        if event is None:
            skipped_lines += 1
            continue

        total += 1
        level = event["level"]
        source = event["source"]

        level_counts[level] += 1
        source_counts[source] = source_counts.get(source, 0) + 1

        if level == "ERROR" or level == "CRITICAL":
            error_counts[source] = error_counts.get(source, 0) + 1

        timestamp = parse_timestamp(event["timestamp"])

        if first is None or timestamp < first:
            first = timestamp

        if last is None or timestamp > last:
            last = timestamp

    remaining = error_counts.copy()
    top_5 = []

    while remaining and len(top_5) < 5:
        best_source = None

        for source in remaining:
            if best_source is None or remaining[source] > remaining[best_source]:
                best_source = source

        top_5.append({"source": best_source, "count": remaining[best_source]})
        del remaining[best_source]

    if first is None:
        first_timestamp = None
    else:
        first_timestamp = first.isoformat()

    if last is None:
        last_timestamp = None
    else:
        last_timestamp = last.isoformat()

    return {
        "first_timestamp": first_timestamp,
        "last_timestamp": last_timestamp,
        "total_events": total,
        "skipped_lines": skipped_lines,
        "levels": level_counts,
        "sources": source_counts,
        "top_error_sources": top_5,
    }


def analyze(paths, format_name, skip_invalid=False):
    events = read_files(paths, format_name, skip_invalid)
    return analyze_events(events)