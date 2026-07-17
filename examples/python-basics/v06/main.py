from pathlib import Path

import analysis
from data_io import load_records, write_report
from reporting import build_report


PROJECT_ROOT = Path(__file__).resolve().parent
INPUT_PATH = PROJECT_ROOT / "data" / "study_records.json"
OUTPUT_PATH = PROJECT_ROOT / "output" / "study_report.txt"


def main():
    records = load_records(INPUT_PATH)
    summary = analysis.summarize_records(records)
    report = build_report(summary)
    write_report(OUTPUT_PATH, report)
    print(report, end="")
    print(f"报告文件：{OUTPUT_PATH.relative_to(PROJECT_ROOT).as_posix()}")


if __name__ == "__main__":
    main()
