import json
from pathlib import Path


data_path = Path(__file__).parent / "data" / "study_records.json"
records = json.loads(data_path.read_text(encoding="utf-8"))

print("学习进度")
for record in records:
    completed = int(record["completed_hours"])
    target = int(record["target_hours"])
    progress = completed / target
    print(f"- {record['course']}: {progress:.0%}")
