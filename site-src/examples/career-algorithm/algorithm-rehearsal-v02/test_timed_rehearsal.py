from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from timed_rehearsal import summarize, validate_events, validate_plan


class TimedRehearsalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        root = Path(__file__).parent
        cls.plan = json.loads((root / "plan.json").read_text(encoding="utf-8"))
        cls.events = json.loads((root / "events.json").read_text(encoding="utf-8"))

    def test_sample_timeline_has_replayable_summary(self) -> None:
        plan = validate_plan(self.plan)
        events = validate_events(self.events, plan)
        lines = summarize(plan, events)
        self.assertIn("task=boundary-search status=switched minutes=15", lines[3])
        self.assertEqual(lines[-2], "summary completed=2 switched=1 remaining=2")

    def test_non_monotonic_event_time_is_rejected(self) -> None:
        events = copy.deepcopy(self.events)
        events["events"][2]["minute"] = 7
        with self.assertRaisesRegex(ValueError, "non-decreasing"):
            validate_events(events, validate_plan(self.plan))

    def test_event_after_budget_is_rejected(self) -> None:
        events = copy.deepcopy(self.events)
        events["events"][-1]["minute"] = 46
        with self.assertRaisesRegex(ValueError, "exceeds"):
            validate_events(events, validate_plan(self.plan))

    def test_second_task_cannot_start_while_one_is_active(self) -> None:
        events = copy.deepcopy(self.events)
        events["events"].insert(
            1,
            {"minute": 2, "type": "start", "task_id": "graph-shortest", "note": "bad-overlap"},
        )
        with self.assertRaisesRegex(ValueError, "another task"):
            validate_events(events, validate_plan(self.plan))

    def test_terminal_event_must_match_active_task(self) -> None:
        events = copy.deepcopy(self.events)
        events["events"][1]["task_id"] = "graph-shortest"
        with self.assertRaisesRegex(ValueError, "active task"):
            validate_events(events, validate_plan(self.plan))

    def test_every_decision_needs_evidence_note(self) -> None:
        events = copy.deepcopy(self.events)
        events["events"][4]["note"] = ""
        with self.assertRaisesRegex(ValueError, "evidence note"):
            validate_events(events, validate_plan(self.plan))

    def test_checkpoints_stay_inside_budget(self) -> None:
        plan = copy.deepcopy(self.plan)
        plan["checkpoints"] = [10, 45]
        with self.assertRaisesRegex(ValueError, "inside budget"):
            validate_plan(plan)


if __name__ == "__main__":
    unittest.main()
