def find_first(values, target):
    comparisons = 0
    for index, value in enumerate(values):
        comparisons += 1
        if value == target:
            return index, comparisons
    return None, comparisons


def main():
    hours = [2, 5, 3, 4]

    print(f"数据：{hours}")
    print(f"下标 2：{hours[2]}")

    index, comparisons = find_first(hours, 3)
    print(f"查找 3：下标 {index}，比较 {comparisons} 次")

    missing_index, missing_comparisons = find_first(hours, 9)
    print(
        f"查找 9：下标 {missing_index}，"
        f"比较 {missing_comparisons} 次"
    )

    try:
        hours[len(hours)]
    except IndexError as error:
        print(f"边界：{type(error).__name__}")


if __name__ == "__main__":
    main()

