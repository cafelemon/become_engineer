#include "traceable_linear_structures_lab/structures.hpp"

#include <concepts>
#include <cstdlib>
#include <iostream>
#include <optional>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace lab = traceable_linear_structures_lab;

static_assert(!std::copy_constructible<lab::SinglyLinkedList>);
static_assert(std::movable<lab::SinglyLinkedList>);
static_assert(!std::copy_constructible<lab::LinkedStack>);
static_assert(std::movable<lab::LinkedStack>);
static_assert(!std::copy_constructible<lab::LinkedQueue>);
static_assert(std::movable<lab::LinkedQueue>);

namespace {

void expect(const bool condition, const std::string& message) {
    if (!condition) {
        std::cerr << "FAILED: " << message << '\n';
        std::exit(1);
    }
}

template <typename Operation>
void expect_out_of_range(Operation operation) {
    try {
        operation();
    } catch (const std::out_of_range&) {
        return;
    }
    expect(false, "expected std::out_of_range");
}

}  // namespace

int main() {
    lab::SinglyLinkedList linked{7, 3, 9, 3};
    linked.push_front(1);
    expect(linked.to_vector() == std::vector{1, 7, 3, 9, 3}, "push front and append order");
    expect(linked.find(3) == lab::FindTrace{2, 3}, "first matching node trace");
    expect(linked.find(8) == lab::FindTrace{std::nullopt, 5}, "missing node visits every node");
    expect(linked.remove_first(1), "remove head");
    expect(linked.remove_first(9), "remove middle");
    expect(linked.remove_first(3), "remove first duplicate");
    expect(linked.to_vector() == std::vector{7, 3}, "remove result");
    expect(!linked.remove_first(8), "missing remove");

    lab::SinglyLinkedList moved = std::move(linked);
    expect(moved.to_vector() == std::vector{7, 3}, "linked list move preserves values");
    expect(linked.empty() && linked.size() == 0, "moved-from linked list is empty");

    lab::SinglyLinkedList empty_linked;
    expect_out_of_range([&empty_linked] { static_cast<void>(empty_linked.pop_front()); });
    expect(empty_linked.empty(), "linked underflow preserves state");

    lab::LinkedStack stack{7, 3, 9};
    expect(stack.peek() == 9 && stack.size() == 3, "stack top");
    expect(stack.pop() == 9, "stack pop");
    expect(stack.to_vector() == std::vector{3, 7}, "stack LIFO order");
    lab::LinkedStack moved_stack = std::move(stack);
    expect(moved_stack.to_vector() == std::vector{3, 7}, "stack move preserves values");
    expect(stack.empty() && stack.size() == 0, "moved-from stack is empty");
    const std::vector stack_source{7, 3, 9};
    expect(lab::drain_stack(stack_source) == std::vector{9, 3, 7}, "drain stack");
    expect(stack_source == std::vector{7, 3, 9}, "drain preserves input");
    lab::LinkedStack empty_stack;
    expect_out_of_range([&empty_stack] { static_cast<void>(empty_stack.pop()); });
    expect_out_of_range([&empty_stack] { static_cast<void>(empty_stack.peek()); });
    expect(empty_stack.empty(), "stack underflow preserves state");

    lab::LinkedQueue queue;
    queue.enqueue(7);
    expect(queue.front() == 7 && queue.back() == 7, "singleton queue endpoints");
    expect(queue.dequeue() == 7 && queue.empty(), "dequeue singleton");
    queue.enqueue(3);
    queue.enqueue(9);
    expect(queue.front() == 3 && queue.back() == 9, "queue reusable after empty");
    expect(queue.to_vector() == std::vector{3, 9}, "queue FIFO order");
    lab::LinkedQueue moved_queue = std::move(queue);
    expect(moved_queue.to_vector() == std::vector{3, 9}, "queue move preserves values");
    expect(queue.empty() && queue.size() == 0, "moved-from queue is empty");
    const std::vector queue_source{7, 3, 9};
    expect(lab::serve_until_empty(queue_source) == queue_source, "serve queue FIFO");
    expect(queue_source == std::vector{7, 3, 9}, "serve preserves input");
    lab::LinkedQueue empty_queue;
    expect_out_of_range([&empty_queue] { static_cast<void>(empty_queue.dequeue()); });
    expect_out_of_range([&empty_queue] { static_cast<void>(empty_queue.front()); });
    expect_out_of_range([&empty_queue] { static_cast<void>(empty_queue.back()); });
    expect(empty_queue.empty(), "queue underflow preserves state");

    expect(lab::build_linked_report() ==
        "可追踪线性结构实验\n链表：7 -> 3 -> 9\nfind=3：index=1，visits=2\npop_front=7\nremaining：3 -> 9", "linked report");
    expect(lab::build_stack_report() ==
        "栈实验\npush：7, 3, 9\ntop=9，size=3\npop=9\nremaining(top->bottom)：3, 7", "stack report");
    expect(lab::build_queue_report() ==
        "队列实验\nenqueue：7, 3, 9\nfront=7，back=9，size=3\ndequeue=7\nremaining(front->back)：3, 9", "queue report");
    return 0;
}
