def calculate_progress_wrong(target_hours, finished_hours):
    return finished_hours / target_hours


def validate_target_hours(value):
    if value <= 0:
        raise ValueError("target_hours 必须大于 0")


wrong_result = calculate_progress_wrong(2, 3)
print(f"错误结果：{wrong_result}（规则上限应为 1.0）")

try:
    validate_target_hours(0)
except ValueError as error:
    print(f"已知输入错误：{error}")
