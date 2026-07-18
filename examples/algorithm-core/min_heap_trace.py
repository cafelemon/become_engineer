def push(heap: list[int], value: int) -> tuple[int, int]:
    heap.append(value)
    index = len(heap) - 1
    comparisons = swaps = 0
    print(f"append={value} heap={heap}")
    while index > 0:
        parent = (index - 1) // 2
        comparisons += 1
        print(f"  compare child={heap[index]} parent={heap[parent]}")
        if heap[index] >= heap[parent]:
            break
        heap[index], heap[parent] = heap[parent], heap[index]
        swaps += 1
        index = parent
        print(f"  swap heap={heap}")
    return comparisons, swaps


heap: list[int] = []
comparisons = swaps = 0
for item in (7, 3, 9, 1, 5):
    step_comparisons, step_swaps = push(heap, item)
    comparisons += step_comparisons
    swaps += step_swaps

print(f"built={heap} comparisons={comparisons} swaps={swaps}")
removed = heap[0]
last = heap.pop()
if heap:
    heap[0] = last
    index = 0
    pop_comparisons = pop_swaps = 0
    while 2 * index + 1 < len(heap):
        child = 2 * index + 1
        right = child + 1
        if right < len(heap):
            pop_comparisons += 1
            if heap[right] < heap[child]:
                child = right
        pop_comparisons += 1
        print(f"down compare current={heap[index]} child={heap[child]}")
        if heap[child] >= heap[index]:
            break
        heap[index], heap[child] = heap[child], heap[index]
        pop_swaps += 1
        index = child
        print(f"down swap heap={heap}")
print(f"removed={removed} remaining={heap} comparisons={pop_comparisons} swaps={pop_swaps}")
