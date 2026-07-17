def calculate_progress(target_hours, finished_hours):
    return min(finished_hours / target_hours, 1.0)


def build_status(target_hours, finished_hours):
    if finished_hours >= target_hours:
        return "已完成"
    return f"还需 {target_hours - finished_hours:g} 小时"


def normalize_tags(records):
    tags = set()
    for record in records:
        tags.update(record["tags"])
    return sorted(tags)


def summarize_records(records):
    total_target = 0
    total_finished = 0
    course_lines = []

    for record in records:
        target = record["target_hours"]
        finished = record["finished_hours"]
        total_target += target
        total_finished += finished
        progress = calculate_progress(target, finished)
        status = build_status(target, finished)
        course_lines.append(
            f'- {record["course"]}: {progress:.0%}，{status}'
        )

    return (
        total_target,
        total_finished,
        tuple(course_lines),
        tuple(normalize_tags(records)),
    )


records = [
    {
        "course": "Python 起步",
        "target_hours": 5,
        "finished_hours": 3,
        "tags": ["Python", "起步", "工具"],
    },
    {
        "course": "复盘练习",
        "target_hours": 2,
        "finished_hours": 2,
        "tags": ["Python", "复盘"],
    },
    {
        "course": "Git 复习",
        "target_hours": 3,
        "finished_hours": 3,
        "tags": ["工具", "复盘"],
    },
]

total_target, total_finished, course_lines, tags = summarize_records(records)

print("学习进度报告")
print(f"总计划：{total_target:g} 小时")
print(f"总完成：{total_finished:g} 小时")
print("课程状态：")
for line in course_lines:
    print(line)
print(f'唯一标签：{", ".join(tags)}')
