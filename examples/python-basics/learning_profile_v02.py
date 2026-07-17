name = "小码"
course = "Python 起步"
weekly_hours = 5
finished_hours = 3
ran_program = True

if finished_hours >= weekly_hours:
    status = "已完成"
else:
    status = "进行中"

print("学习档案")
print("昵称：", name)
print("课程：", course)
print("本周计划：", weekly_hours, "小时")
print("本周完成：", finished_hours, "小时")
print("状态：", status)

if status == "进行中":
    print("还需：", weekly_hours - finished_hours, "小时")

print("本周行动：")
actions = ["继续学习", "运行代码", "记录结果"]
for number in range(1, len(actions) + 1):
    print(number, actions[number - 1])

ready_for_review = finished_hours >= weekly_hours and ran_program
print("可以复盘：", ready_for_review)
