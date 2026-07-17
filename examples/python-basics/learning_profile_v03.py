def calculate_progress(target_hours, finished_hours):
    return min(finished_hours / target_hours, 1.0)


def build_status(target_hours, finished_hours):
    if finished_hours >= target_hours:
        return "已完成"
    return f"还需 {target_hours - finished_hours:g} 小时"


def build_report_line(course, target_hours, finished_hours, prefix="- "):
    progress = calculate_progress(target_hours, finished_hours)
    status = build_status(target_hours, finished_hours)
    return f"{prefix}{course}: {progress:.0%}，{status}"


name = "小码"
course = "Python 起步"
weekly_hours = 5
finished_hours = 3

print("学习档案")
print("昵称：", name)
print(build_report_line(course, weekly_hours, finished_hours))
print(build_report_line("复盘练习", 2, 2, prefix="* "))
