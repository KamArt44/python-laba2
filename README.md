# Активация виртуального окружения: .\.venv\Scripts\Activate.ps1
# Помощь: python -m streamstats --help

# Лабораторная работа 2

Программа `streamstats` читает файлы CSV и JSONL. Считает колличество событий по уровням и источникам, находит первую и последнюю дату, а также топ-5 источников ошибок.

Нужен Python 3.11 или новее.

## Установка

Команды нужно выполнять в папке проекта, где находится `pyproject.toml`.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

Первая команда создаёт окружение, вторая активирует его, третья устанавливает проект и инструменты проверки.

## Запуск

Обработка JSONL:

```powershell
python -m streamstats analyze examples/events.jsonl --format jsonl
```

Эта команда обрабатывает CSV и сохроняет отчёт в файл:

```powershell
python -m streamstats analyze examples/events.csv --format csv --output report.json
```

Без `--output` результат выводится в терминал. Если добавить `--skip-invalid`, программа будет пропускать неправильные записи. По умолчанию она останавливается на первой ошибке.

## Проверка

```powershell
python -m pytest
python -m ruff check .
```

`pytest` запускает тесты, а `ruff` проверяет код.