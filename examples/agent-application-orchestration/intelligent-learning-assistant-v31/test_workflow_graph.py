import unittest

from workflow_graph import Request, Run, choose_mode, execute


class WorkflowGraphTests(unittest.TestCase):
    def test_known_answer_uses_deterministic_workflow(self):
        run = execute(Request("alice", "ACL", "answer"), allowed_actions={"answer"})
        self.assertEqual(("workflow", "completed"), (run.mode, run.terminal))

    def test_tool_request_uses_router(self):
        run = execute(Request("alice", "health", "diagnostic"), allowed_actions={"diagnostic"})
        self.assertEqual("router", run.mode)
        self.assertIn("tool_selected", run.steps)

    def test_unknown_request_uses_bounded_agent(self):
        self.assertEqual("agent", choose_mode(Request("alice", "investigate", "open")))

    def test_default_deny_happens_before_retrieval(self):
        run = execute(Request("alice", "secret", "delete"), allowed_actions={"answer"})
        self.assertEqual("refused", run.terminal)
        self.assertNotIn("retrieved", run.steps)

    def test_empty_evidence_refuses(self):
        run = execute(Request("alice", "", "answer"), allowed_actions={"answer"})
        self.assertEqual("refused", run.terminal)

    def test_invalid_transition_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "invalid_transition"):
            Run("workflow", Request("alice", "x")).transition("authorized", "answered")

    def test_agent_unknown_choice_fails_closed(self):
        run = execute(Request("alice", "x", "open"), allowed_actions={"open"}, scripted_choices=["invent_tool"])
        self.assertEqual("failed", run.terminal)

    def test_step_budget_stops_loop(self):
        run = execute(Request("alice", "x", "open"), allowed_actions={"open"}, scripted_choices=["inspect"] * 20)
        self.assertEqual("budget_exhausted", run.terminal)
        self.assertLessEqual(len(run.steps), run.max_steps)


if __name__ == "__main__":
    unittest.main()
