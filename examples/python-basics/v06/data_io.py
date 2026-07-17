import json


def load_records(input_path):
    text = input_path.read_text(encoding="utf-8")
    document = json.loads(text)
    return document["records"]


def write_report(output_path, report):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
