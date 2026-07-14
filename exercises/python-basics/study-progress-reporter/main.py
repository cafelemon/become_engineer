import json
import sys
from pathlib import Path

from analysis import summarize_records
from data_io import find_json_files, load_records, write_report
from reporting import build_report


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
INPUT_PATH = DATA_DIR / "study_records.json"
OUTPUT_PATH = PROJECT_ROOT / "output" / "study_report.txt"


def run(input_path=INPUT_PATH, data_dir=DATA_DIR, output_path=OUTPUT_PATH):
    json_files = find_json_files(data_dir)
    print("发现的数据文件：")
    for path in json_files:
        print(f"- {path.name}")

    records = load_records(input_path)
    summary = summarize_records(records)
    report = build_report(summary)
    write_report(output_path, report)
    print(report, end="")
    print(f"报告已写入：{output_path}")
    return report


def main(input_path=INPUT_PATH, data_dir=DATA_DIR, output_path=OUTPUT_PATH):
    try:
        run(input_path, data_dir, output_path)
    except FileNotFoundError as error:
        print(f"输入错误：找不到文件 {error.filename}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as error:
        print(
            f"输入错误：JSON 格式无效，第 {error.lineno} 行，"
            f"第 {error.colno} 列",
            file=sys.stderr,
        )
        return 1
    except ValueError as error:
        print(f"输入错误：{error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

