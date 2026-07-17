def calculate_progress(target_hours, finished_hours):
    return min(finished_hours / target_hours, 1.0)


def build_status(target_hours, finished_hours):
    if finished_hours >= target_hours:
        return "已完成"
    return f"还需 {target_hours - finished_hours:g} 小时"


def summarize_records(records):
    total_target = 0
    total_finished = 0
    course_lines = []
    tags = set()

    for record in records:
        target = record["target_hours"]
        finished = record["finished_hours"]
        total_target += target
        total_finished += finished
        tags.update(record["tags"])
        course_lines.append(
            f'- {record["course"]}: '
            f"{calculate_progress(target, finished):.0%}，"
            f"{build_status(target, finished)}"
        )

    return (
        total_target,
        total_finished,
        tuple(course_lines),
        tuple(sorted(tags)),
    )
