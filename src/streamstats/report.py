
import json


def write_report(report: dict, output: str | None = None) -> None:
    if output is None:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        with open(output, "w", encoding="utf-8") as file:
            json.dump(report, file, ensure_ascii=False, indent=2)
            file.write("\n")
