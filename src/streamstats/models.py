"""Проверка событий"""

from datetime import UTC, datetime

from streamstats.errors import InvalidEventError, InvalidTimestampError

FIELDS = ("timestamp", "level", "source", "message")
LEVELS = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")


def parse_timestamp(text):
    try:
        timestamp = datetime.fromisoformat(text)

        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=UTC)

        return timestamp.astimezone(UTC)

    except (ValueError, OverflowError):
        raise InvalidTimestampError ("Неверное время")


def validate_event(event):
    if not isinstance(event, dict):
        raise InvalidEventError("Событие должно быть словарём")

    for field in FIELDS:
        if field not in event:
            raise InvalidEventError(f"Отсутствует поле {field}")

        if not isinstance(event[field], str):
            raise InvalidEventError(f"Поле {field} должно быть строкой")

    if event["source"].strip() == "":
        raise InvalidEventError("Поле source не должно быть пустым")

    if event["level"] not in LEVELS:
        raise InvalidEventError(f"Неизвестный уровень: {event['level']}")

    parse_timestamp(event["timestamp"])
    return True
