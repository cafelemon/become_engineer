import json
from pathlib import Path


REQUIRED_FIELDS = ("course", "target_hours", "finished_hours", "tags")


def find_json_files(data_dir):
    return sorted(data_dir.glob("*.json"))


def _validate_number(value, field_name, record_number):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(
            f"第 {record_number} 条记录的 {field_name} 必须是数字"
        )


def validate_document(document):
    if not isinstance(document, dict):
        raise ValueError("JSON 根结构必须是对象")
    if "records" not in document:
        raise ValueError("JSON 根对象缺少 records 字段")

    records = document["records"]
    if not isinstance(records, list):
        raise ValueError("records 必须是列表")

    for index, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            raise ValueError(f"第 {index} 条记录必须是对象")

        for field_name in REQUIRED_FIELDS:
            if field_name not in record:
                raise ValueError(
                    f"第 {index} 条记录缺少 {field_name} 字段"
                )

        if not isinstance(record["course"], str) or not record["course"].strip():
            raise ValueError(f"第 {index} 条记录的 course 必须是非空字符串")

        _validate_number(record["target_hours"], "target_hours", index)
        _validate_number(record["finished_hours"], "finished_hours", index)

        if record["target_hours"] <= 0:
            raise ValueError(f"第 {index} 条记录的 target_hours 必须大于 0")
        if record["finished_hours"] < 0:
            raise ValueError(
                f"第 {index} 条记录的 finished_hours 不能小于 0"
            )

        tags = record["tags"]
        if not isinstance(tags, list) or not all(
            isinstance(tag, str) for tag in tags
        ):
            raise ValueError(f"第 {index} 条记录的 tags 必须是字符串列表")

    return records


def load_records(input_path):
    text = input_path.read_text(encoding="utf-8")
    document = json.loads(text)
    return validate_document(document)


def write_report(output_path, report):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")

