#include "traceable_linear_structures_lab/structures.hpp"

#include <sstream>
#include <stdexcept>
#include <utility>

namespace traceable_linear_structures_lab {
namespace {

std::string join(const std::vector<int>& values, const std::string& separator) {
    std::ostringstream output;
    for (std::size_t index = 0; index < values.size(); ++index) {
        if (index != 0) {
            output << separator;
        }
        output << values[index];
    }
    return output.str();
}

}  // namespace

SinglyLinkedList::SinglyLinkedList(std::initializer_list<int> values) {
    for (const int value : values) {
        append(value);
    }
}

SinglyLinkedList::SinglyLinkedList(SinglyLinkedList&& other) noexcept
    : head_(std::move(other.head_)), size_(std::exchange(other.size_, 0)) {}

SinglyLinkedList& SinglyLinkedList::operator=(SinglyLinkedList&& other) noexcept {
    if (this != &other) {
        head_ = std::move(other.head_);
        size_ = std::exchange(other.size_, 0);
    }
    return *this;
}

void SinglyLinkedList::push_front(const int value) {
    head_ = std::make_unique<Node>(Node{value, std::move(head_)});
    ++size_;
}

void SinglyLinkedList::append(const int value) {
    auto new_node = std::make_unique<Node>(Node{value, nullptr});
    if (head_ == nullptr) {
        head_ = std::move(new_node);
    } else {
        Node* current = head_.get();
        while (current->next != nullptr) {
            current = current->next.get();
        }
        current->next = std::move(new_node);
    }
    ++size_;
}

int SinglyLinkedList::pop_front() {
    if (head_ == nullptr) {
        throw std::out_of_range("pop_front from empty linked list");
    }
    const int value = head_->value;
    head_ = std::move(head_->next);
    --size_;
    return value;
}

FindTrace SinglyLinkedList::find(const int value) const noexcept {
    const Node* current = head_.get();
    std::size_t visits = 0;
    while (current != nullptr) {
        ++visits;
        if (current->value == value) {
            return {visits - 1, visits};
        }
        current = current->next.get();
    }
    return {std::nullopt, visits};
}

bool SinglyLinkedList::remove_first(const int value) noexcept {
    std::unique_ptr<Node>* link = &head_;
    while (*link != nullptr) {
        if ((*link)->value == value) {
            *link = std::move((*link)->next);
            --size_;
            return true;
        }
        link = &((*link)->next);
    }
    return false;
}

std::vector<int> SinglyLinkedList::to_vector() const {
    std::vector<int> result;
    result.reserve(size_);
    const Node* current = head_.get();
    while (current != nullptr) {
        result.push_back(current->value);
        current = current->next.get();
    }
    return result;
}

std::size_t SinglyLinkedList::size() const noexcept { return size_; }

bool SinglyLinkedList::empty() const noexcept { return head_ == nullptr; }

LinkedStack::LinkedStack(std::initializer_list<int> values) {
    for (const int value : values) {
        push(value);
    }
}

LinkedStack::LinkedStack(LinkedStack&& other) noexcept
    : head_(std::move(other.head_)), size_(std::exchange(other.size_, 0)) {}

LinkedStack& LinkedStack::operator=(LinkedStack&& other) noexcept {
    if (this != &other) {
        head_ = std::move(other.head_);
        size_ = std::exchange(other.size_, 0);
    }
    return *this;
}

void LinkedStack::push(const int value) {
    head_ = std::make_unique<Node>(Node{value, std::move(head_)});
    ++size_;
}

int LinkedStack::pop() {
    if (head_ == nullptr) {
        throw std::out_of_range("pop from empty stack");
    }
    const int value = head_->value;
    head_ = std::move(head_->next);
    --size_;
    return value;
}

int LinkedStack::peek() const {
    if (head_ == nullptr) {
        throw std::out_of_range("peek from empty stack");
    }
    return head_->value;
}

std::vector<int> LinkedStack::to_vector() const {
    std::vector<int> result;
    result.reserve(size_);
    const Node* current = head_.get();
    while (current != nullptr) {
        result.push_back(current->value);
        current = current->next.get();
    }
    return result;
}

std::size_t LinkedStack::size() const noexcept { return size_; }

bool LinkedStack::empty() const noexcept { return head_ == nullptr; }

LinkedQueue::LinkedQueue(std::initializer_list<int> values) {
    for (const int value : values) {
        enqueue(value);
    }
}

LinkedQueue::LinkedQueue(LinkedQueue&& other) noexcept
    : head_(std::move(other.head_)), tail_(std::exchange(other.tail_, nullptr)), size_(std::exchange(other.size_, 0)) {}

LinkedQueue& LinkedQueue::operator=(LinkedQueue&& other) noexcept {
    if (this != &other) {
        head_ = std::move(other.head_);
        tail_ = std::exchange(other.tail_, nullptr);
        size_ = std::exchange(other.size_, 0);
    }
    return *this;
}

void LinkedQueue::enqueue(const int value) {
    auto new_node = std::make_unique<Node>(Node{value, nullptr});
    Node* const new_tail = new_node.get();
    if (tail_ == nullptr) {
        head_ = std::move(new_node);
    } else {
        tail_->next = std::move(new_node);
    }
    tail_ = new_tail;
    ++size_;
}

int LinkedQueue::dequeue() {
    if (head_ == nullptr) {
        throw std::out_of_range("dequeue from empty queue");
    }
    const int value = head_->value;
    head_ = std::move(head_->next);
    --size_;
    if (head_ == nullptr) {
        tail_ = nullptr;
    }
    return value;
}

int LinkedQueue::front() const {
    if (head_ == nullptr) {
        throw std::out_of_range("front from empty queue");
    }
    return head_->value;
}

int LinkedQueue::back() const {
    if (tail_ == nullptr) {
        throw std::out_of_range("back from empty queue");
    }
    return tail_->value;
}

std::vector<int> LinkedQueue::to_vector() const {
    std::vector<int> result;
    result.reserve(size_);
    const Node* current = head_.get();
    while (current != nullptr) {
        result.push_back(current->value);
        current = current->next.get();
    }
    return result;
}

std::size_t LinkedQueue::size() const noexcept { return size_; }

bool LinkedQueue::empty() const noexcept { return head_ == nullptr; }

std::vector<int> drain_stack(const std::vector<int>& values) {
    LinkedStack stack;
    for (const int value : values) {
        stack.push(value);
    }
    std::vector<int> result;
    result.reserve(values.size());
    while (!stack.empty()) {
        result.push_back(stack.pop());
    }
    return result;
}

std::vector<int> serve_until_empty(const std::vector<int>& values) {
    LinkedQueue queue;
    for (const int value : values) {
        queue.enqueue(value);
    }
    std::vector<int> result;
    result.reserve(values.size());
    while (!queue.empty()) {
        result.push_back(queue.dequeue());
    }
    return result;
}

std::string build_linked_report() {
    SinglyLinkedList values{7, 3, 9};
    const FindTrace trace = values.find(3);
    std::ostringstream output;
    output << "可追踪线性结构实验\n"
           << "链表：" << join(values.to_vector(), " -> ") << '\n'
           << "find=3：index=" << *trace.index << "，visits=" << trace.visits << '\n'
           << "pop_front=" << values.pop_front() << '\n'
           << "remaining：" << join(values.to_vector(), " -> ");
    return output.str();
}

std::string build_stack_report() {
    LinkedStack stack{7, 3, 9};
    std::ostringstream output;
    output << "栈实验\n"
           << "push：7, 3, 9\n"
           << "top=" << stack.peek() << "，size=" << stack.size() << '\n'
           << "pop=" << stack.pop() << '\n'
           << "remaining(top->bottom)：" << join(stack.to_vector(), ", ");
    return output.str();
}

std::string build_queue_report() {
    LinkedQueue queue{7, 3, 9};
    std::ostringstream output;
    output << "队列实验\n"
           << "enqueue：7, 3, 9\n"
           << "front=" << queue.front() << "，back=" << queue.back() << "，size=" << queue.size() << '\n'
           << "dequeue=" << queue.dequeue() << '\n'
           << "remaining(front->back)：" << join(queue.to_vector(), ", ");
    return output.str();
}

}  // namespace traceable_linear_structures_lab
