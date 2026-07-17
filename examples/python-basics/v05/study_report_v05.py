import json
from pathlib import Path


def calculate_progress(target_hours, finished_hours):
    return min(finished_hours / target_hours, 1.0)


def build_status(target_hours, finished_hours):
    if finished_hours >= target_hours:
        return "已完成"
    return f"还需 {target_hours - finished_hours:g} 小时"


def load_records(input_path):
    text = input_path.read_text(encoding="utf-8")
    document = json.loads(text)
    return document["records"]


def build_report(records):
    total_target = 0
    total_finished = 0
    tags = set()
    lines = ["学习进度报告", "课程状态："]

    for record in records:
        target = record["target_hours"]
        finished = record["finished_hours"]
        total_target += target
        total_finished += finished
        tags.update(record["tags"])
        lines.append(
            f'- {record["course"]}: '
            f"{calculate_progress(target, finished):.0%}，"
            f"{build_status(target, finished)}"
        )

    lines.insert(1, f"总计划：{total_target:g} 小时")
    lines.insert(2, f"总完成：{total_finished:g} 小时")
    lines.append(f'唯一标签：{", ".join(sorted(tags)) if tags else "无"}')
    return "\n".join(lines) + "\n"


def main():
    data_dir = Path("data")
    input_path = data_dir / "study_records.json"
    output_path = Path("output") / "study_report.txt"

    json_files = sorted(data_dir.glob("*.json"))
    print("发现 JSON：" + ", ".join(path.name for path in json_files))

    records = load_records(input_path)
    report = build_report(records)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")

    print(report, end="")
    print(f"报告文件：{output_path.as_posix()}")


if __name__ == "__main__":
    main()
