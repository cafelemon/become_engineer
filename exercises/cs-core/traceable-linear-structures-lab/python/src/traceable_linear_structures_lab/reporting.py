from traceable_linear_structures_lab.structures import LinkedQueue, LinkedStack, SinglyLinkedList


def _join(values: list[int], separator: str) -> str:
    return separator.join(str(value) for value in values)


def build_linked_report() -> str:
    values = SinglyLinkedList((7, 3, 9))
    trace = values.find(3)
    index = "missing" if trace.index is None else str(trace.index)
    lines = [
        "可追踪线性结构实验",
        f"链表：{_join(values.to_list(), ' -> ')}",
        f"find=3：index={index}，visits={trace.visits}",
        f"pop_front={values.pop_front()}",
        f"remaining：{_join(values.to_list(), ' -> ')}",
    ]
    return "\n".join(lines)


def build_stack_report() -> str:
    stack = LinkedStack((7, 3, 9))
    lines = [
        "栈实验",
        "push：7, 3, 9",
        f"top={stack.peek()}，size={stack.size()}",
        f"pop={stack.pop()}",
        f"remaining(top->bottom)：{_join(stack.to_list(), ', ')}",
    ]
    return "\n".join(lines)


def build_queue_report() -> str:
    queue = LinkedQueue((7, 3, 9))
    lines = [
        "队列实验",
        "enqueue：7, 3, 9",
        f"front={queue.front()}，back={queue.back()}，size={queue.size()}",
        f"dequeue={queue.dequeue()}",
        f"remaining(front->back)：{_join(queue.to_list(), ', ')}",
    ]
    return "\n".join(lines)
