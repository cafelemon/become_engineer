import unittest

from task_planning import Plan, Task, apply_result, classify_failure, ready_tasks, replan, terminal, validate


class TaskPlanningTests(unittest.TestCase):
    def plan(self):
        return Plan("goal", (Task("a", "retrieve"), Task("b", "summarize", ("a",), 2)))

    def test_valid_dependency_plan(self):
        validate(self.plan())
        self.assertEqual(("a",), tuple(task.task_id for task in ready_tasks(self.plan())))

    def test_unknown_action_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "invalid_task"):
            validate(Plan("x", (Task("a", "shell"),)))

    def test_dependency_cycle_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "dependency_cycle"):
            validate(Plan("x", (Task("a", "retrieve", ("b",)), Task("b", "draft", ("a",)))))

    def test_task_count_and_budget_are_bounded(self):
        with self.assertRaisesRegex(ValueError, "total_budget"):
            validate(Plan("x", (Task("a", "retrieve", budget=20),), total_budget=12))

    def test_dependency_unblocks_after_completion(self):
        plan = apply_result(self.plan(), "a", success=True)
        self.assertEqual(("b",), tuple(task.task_id for task in ready_tasks(plan)))

    def test_retryable_failure_uses_task_budget(self):
        plan = apply_result(self.plan(), "b", success=False, failure_code="timeout")
        self.assertEqual("pending", plan.tasks[1].status)
        plan = apply_result(plan, "b", success=False, failure_code="timeout")
        self.assertEqual("failed", plan.tasks[1].status)

    def test_completed_tasks_are_immutable_during_replan(self):
        plan = apply_result(self.plan(), "a", success=True)
        with self.assertRaisesRegex(ValueError, "completed_task_immutable"):
            replan(plan, (Task("a", "draft"),))

    def test_terminal_states_are_explicit(self):
        failed = apply_result(Plan("x", (Task("a", "retrieve"),)), "a", success=False, failure_code="permission_denied")
        self.assertEqual("failed", terminal(failed))
        completed = apply_result(Plan("x", (Task("a", "retrieve"),)), "a", success=True)
        self.assertEqual("completed", terminal(completed))
        self.assertEqual("terminal", classify_failure("permission_denied"))


if __name__ == "__main__":
    unittest.main()
