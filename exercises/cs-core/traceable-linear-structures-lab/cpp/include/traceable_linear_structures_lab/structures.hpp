#pragma once

#include <cstddef>
#include <initializer_list>
#include <memory>
#include <optional>
#include <string>
#include <vector>

namespace traceable_linear_structures_lab {

struct FindTrace {
    std::optional<std::size_t> index;
    std::size_t visits;
    bool operator==(const FindTrace&) const = default;
};

class SinglyLinkedList {
public:
    SinglyLinkedList() = default;
    SinglyLinkedList(std::initializer_list<int> values);
    ~SinglyLinkedList() = default;
    SinglyLinkedList(const SinglyLinkedList&) = delete;
    SinglyLinkedList& operator=(const SinglyLinkedList&) = delete;
    SinglyLinkedList(SinglyLinkedList&& other) noexcept;
    SinglyLinkedList& operator=(SinglyLinkedList&& other) noexcept;

    void push_front(int value);
    void append(int value);
    [[nodiscard]] int pop_front();
    [[nodiscard]] FindTrace find(int value) const noexcept;
    [[nodiscard]] bool remove_first(int value) noexcept;
    [[nodiscard]] std::vector<int> to_vector() const;
    [[nodiscard]] std::size_t size() const noexcept;
    [[nodiscard]] bool empty() const noexcept;

private:
    struct Node {
        int value;
        std::unique_ptr<Node> next;
    };

    std::unique_ptr<Node> head_;
    std::size_t size_ = 0;
};

class LinkedStack {
public:
    LinkedStack() = default;
    LinkedStack(std::initializer_list<int> values);
    ~LinkedStack() = default;
    LinkedStack(const LinkedStack&) = delete;
    LinkedStack& operator=(const LinkedStack&) = delete;
    LinkedStack(LinkedStack&& other) noexcept;
    LinkedStack& operator=(LinkedStack&& other) noexcept;

    void push(int value);
    [[nodiscard]] int pop();
    [[nodiscard]] int peek() const;
    [[nodiscard]] std::vector<int> to_vector() const;
    [[nodiscard]] std::size_t size() const noexcept;
    [[nodiscard]] bool empty() const noexcept;

private:
    struct Node {
        int value;
        std::unique_ptr<Node> next;
    };

    std::unique_ptr<Node> head_;
    std::size_t size_ = 0;
};

class LinkedQueue {
public:
    LinkedQueue() = default;
    LinkedQueue(std::initializer_list<int> values);
    ~LinkedQueue() = default;
    LinkedQueue(const LinkedQueue&) = delete;
    LinkedQueue& operator=(const LinkedQueue&) = delete;
    LinkedQueue(LinkedQueue&& other) noexcept;
    LinkedQueue& operator=(LinkedQueue&& other) noexcept;

    void enqueue(int value);
    [[nodiscard]] int dequeue();
    [[nodiscard]] int front() const;
    [[nodiscard]] int back() const;
    [[nodiscard]] std::vector<int> to_vector() const;
    [[nodiscard]] std::size_t size() const noexcept;
    [[nodiscard]] bool empty() const noexcept;

private:
    struct Node {
        int value;
        std::unique_ptr<Node> next;
    };

    std::unique_ptr<Node> head_;
    Node* tail_ = nullptr;
    std::size_t size_ = 0;
};

[[nodiscard]] std::vector<int> drain_stack(const std::vector<int>& values);
[[nodiscard]] std::vector<int> serve_until_empty(const std::vector<int>& values);
[[nodiscard]] std::string build_linked_report();
[[nodiscard]] std::string build_stack_report();
[[nodiscard]] std::string build_queue_report();

}  // namespace traceable_linear_structures_lab
