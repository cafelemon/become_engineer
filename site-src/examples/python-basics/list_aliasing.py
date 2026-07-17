records = [{"course": "Python 起步"}]

same_list = records
same_list.append({"course": "复盘练习"})
print("直接赋值：", len(records), len(same_list))

outer_copy = records.copy()
outer_copy.append({"course": "Git 复习"})
print("复制外层：", len(records), len(outer_copy))

outer_copy[0]["course"] = "Python 起步（已修改）"
print("内层仍共享：", records[0]["course"])
