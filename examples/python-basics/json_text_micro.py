import json


text = '{"course": "Python 起步", "active": true, "note": null}'
record = json.loads(text)

print(type(record).__name__)
print(record["course"])
print(record["active"], record["note"])
print(json.dumps(record, ensure_ascii=False, indent=2))
