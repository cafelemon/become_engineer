import unittest

from traceable_linear_structures_lab import (
    FindTrace,
    LinkedQueue,
    LinkedStack,
    SinglyLinkedList,
    drain_stack,
    serve_until_empty,
)


class SinglyLinkedListTests(unittest.TestCase):
    def test_empty_and_underflow(self) -> None:
        values = SinglyLinkedList()
        self.assertTrue(values.empty())
        self.assertEqual(values.size(), 0)
        self.assertEqual(values.find(7), FindTrace(None, 0))
        with self.assertRaises(IndexError):
            values.pop_front()
        self.assertEqual(values.to_list(), [])

    def test_head_append_find_and_pop(self) -> None:
        values = SinglyLinkedList((7, 3, 9, 3))
        values.push_front(1)
        self.assertEqual(values.to_list(), [1, 7, 3, 9, 3])
        self.assertEqual(values.find(3), FindTrace(2, 3))
        self.assertEqual(values.find(8), FindTrace(None, 5))
        self.assertEqual(values.pop_front(), 1)
        self.assertEqual(values.size(), 4)

    def test_remove_first_covers_head_middle_tail_and_missing(self) -> None:
        values = SinglyLinkedList((7, 3, 9, 3))
        self.assertTrue(values.remove_first(7))
        self.assertTrue(values.remove_first(9))
        self.assertTrue(values.remove_first(3))
        self.assertEqual(values.to_list(), [3])
        self.assertTrue(values.remove_first(3))
        self.assertFalse(values.remove_first(3))
        self.assertTrue(values.empty())


class LinkedStackTests(unittest.TestCase):
    def test_lifo_and_drain_preserve_input(self) -> None:
        source = [7, 3, 9]
        stack = LinkedStack(source)
        self.assertEqual(stack.to_list(), [9, 3, 7])
        self.assertEqual(stack.peek(), 9)
        self.assertEqual(stack.pop(), 9)
        self.assertEqual(stack.to_list(), [3, 7])
        self.assertEqual(drain_stack(source), [9, 3, 7])
        self.assertEqual(source, [7, 3, 9])

    def test_underflow_does_not_change_state(self) -> None:
        stack = LinkedStack()
        for operation in (stack.pop, stack.peek):
            with self.assertRaises(IndexError):
                operation()
            self.assertEqual(stack.to_list(), [])


class LinkedQueueTests(unittest.TestCase):
    def test_fifo_and_singleton_tail_reset(self) -> None:
        queue = LinkedQueue()
        queue.enqueue(7)
        self.assertEqual(queue.front(), 7)
        self.assertEqual(queue.back(), 7)
        self.assertEqual(queue.dequeue(), 7)
        self.assertTrue(queue.empty())
        queue.enqueue(3)
        queue.enqueue(9)
        self.assertEqual(queue.to_list(), [3, 9])
        self.assertEqual(queue.front(), 3)
        self.assertEqual(queue.back(), 9)

    def test_underflow_and_serve_preserve_input(self) -> None:
        queue = LinkedQueue()
        for operation in (queue.dequeue, queue.front, queue.back):
            with self.assertRaises(IndexError):
                operation()
            self.assertEqual(queue.to_list(), [])
        source = [7, 3, 9]
        self.assertEqual(serve_until_empty(source), source)
        self.assertEqual(source, [7, 3, 9])


if __name__ == "__main__":
    unittest.main()
