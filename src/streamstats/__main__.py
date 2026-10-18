import argparse
import logging
import sys
from pathlib import Path

from .analysis import analyze
from .errors import CLIConfigError, StreamStatsError
from .report import write_report


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise CLIConfigError(message)


def parser():
    parser = Parser(description="Статистика событий из CSV и JSONL")
    commands = parser.add_subparsers(dest="command", required=True)
    analyze_parser = commands.add_parser("analyze", help="проанализировать файлы")
    analyze_parser.add_argument("inputs", nargs="+", help="входные файлы")
    analyze_parser.add_argument("--format", required=True, help="csv или jsonl")
    analyze_parser.add_argument("--output", help="путь к JSON-отчёту")
    analyze_parser.add_argument(
        "--skip-invalid", action="store_true", help="пропускать неверные записи"
    )
    return parser


def main(argv=None) -> int:
    logging.basicConfig(level=logging.WARNING, format="%(levelname)s: %(message)s")
    try:
        args = parser().parse_args(argv)
        if args.output is not None:
            output_path = Path(args.output).resolve()
            for path in args.inputs:
                if output_path == Path(path).resolve():
                    raise CLIConfigError(
                    )

        report = analyze(args.inputs, args.format, args.skip_invalid)
        write_report(report, args.output)
    except (StreamStatsError, OSError, UnicodeError) as error:
        print(f"Ошибка: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
