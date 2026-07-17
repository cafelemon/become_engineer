def show_status(status):
    print(status)


def get_status(status):
    return status


printed_result = show_status("进行中")
returned_result = get_status("进行中")

print("show_status 的调用结果：", printed_result)
print("get_status 的调用结果：", returned_result)
