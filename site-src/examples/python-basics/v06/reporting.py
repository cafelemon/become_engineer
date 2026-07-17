def build_report(summary):
    total_target, total_finished, course_lines, tags = summary
    lines = [
        "学习进度报告",
        f"总计划：{total_target:g} 小时",
        f"总完成：{total_finished:g} 小时",
        "课程状态：",
    ]
    lines.extend(course_lines or ("- 暂无记录",))
    lines.append(f'唯一标签：{", ".join(tags) if tags else "无"}')
    return "\n".join(lines) + "\n"
