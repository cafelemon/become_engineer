def build_profile(name: str, course: str, completed_hours: int, target_hours: int) -> str:
    progress = completed_hours / target_hours
    status = "已达标" if completed_hours >= target_hours else "进行中"
    return (
        "学习档案\n"
        f"昵称：{name}\n"
        f"课程：{course}\n"
        f"进度：{progress:.0%}\n"
        f"状态：{status}"
    )


print(build_profile("小码", "Python 起步", 3, 5))
