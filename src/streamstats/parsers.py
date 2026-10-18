"""Чтение CSV и JSONL по одной записи. None - эт пропуск."""

import csv
import json
import logging
from streamstats.errors import (
    InvalidEventError,
    InvalidTimestampError,
    UnsupportedFormatError,
)
from streamstats.models import FIELDS, validate_event

logger = logging.getLogger(__name__)


def parse_jsonl_line(line):
    try:
        event = json.loads(line)
    except (ValueError, RecursionError) as error:
        raise InvalidEventError("Неверная запись JSON") from error

    if not isinstance(event, dict):
        raise InvalidEventError("В строке ожидается JSON-объект")

    return event


def iter_jsonl_lines(path):
    count = 1

    with open(path, "r", encoding="utf-8-sig") as file:
        for line in file:
            yield count, line.strip()
            count += 1


def handle_invalid(error, path, file_number, line_number, skip_invalid):
    message = f"Файл №{file_number} ({path}), строка {line_number}: {error}"

    if skip_invalid:
        logger.warning(message)
        return

    if isinstance(error, InvalidTimestampError):
        raise InvalidTimestampError(message) from error

    raise InvalidEventError(message) from error


def read_jsonl(path, skip_invalid=False, file_number=1):
    for line_number, line in iter_jsonl_lines(path):
        try:
            event = parse_jsonl_line(line)
            validate_event(event)

        except InvalidEventError as error:
            handle_invalid(error, path, file_number, line_number, skip_invalid)
            yield None
            continue

        yield event


def read_csv(path, skip_invalid=False, file_number=1):
    with open(path, "r", encoding="utf-8-sig", newline="") as file:
        reader = csv.reader(file, strict=True)

        try:
            header = next(reader)
        except StopIteration:
            return
        except csv.Error as error:
            raise InvalidEventError(
                f"Файл №{file_number} ({path}), строка {reader.line_num}: "
                "неверный заголовок CSV"
            ) from error

        for field in FIELDS:
            if field not in header:
                raise InvalidEventError(
                    f"Файл №{file_number} ({path}), строка {reader.line_num}: "
                    f"неверный заголовок CSV: отсутствует поле {field}"
                )

        seen = []
        for name in header:
            if name in seen:
                raise InvalidEventError(
                    f"Файл №{file_number} ({path}), строка {reader.line_num}: "
                    f"повторяющееся имя столбца в заголовке CSV: {name}"
                )
            seen.append(name)

        while True:
            try:
                row = next(reader)

                if len(row) == 0:
                    continue

                if len(row) != len(header):
                    raise InvalidEventError(
                        "Количество значений не совпадает с количеством столбцов"
                    )

                event = {}
                for index in range(len(header)):
                    field = header[index]
                    value = row[index]
                    event[field] = value

                validate_event(event)

            except StopIteration:
                break

            except (InvalidEventError, csv.Error) as error:
                handle_invalid(
                    error, path, file_number, reader.line_num, skip_invalid
                )
                yield None
                continue

            yield event


def read_files(paths, format_name, skip_invalid=False):
    if format_name != "jsonl" and format_name != "csv":
        raise UnsupportedFormatError(f"Неподдерживаемый формат: {format_name}")

    file_number = 1

    for path in paths:
        if format_name == "jsonl":
            events = read_jsonl(path, skip_invalid, file_number)
        else:
            events = read_csv(path, skip_invalid, file_number)

        for event in events:
            yield event

        file_number += 1


def read_jsonl_files(paths, skip_invalid=False):
    return read_files(paths, "jsonl", skip_invalid)
