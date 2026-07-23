from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

import torch

from checkpoint_lab import (
    INTERRUPT_EPOCH,
    TOTAL_EPOCHS,
    TrainingState,
    build_training_objects,
    compare_continuous_and_resumed,
    file_sha256,
    fixed_report,
    load_checkpoint,
    save_checkpoint,
    train_until,
)


class CheckpointLabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        torch.set_num_threads(1)

    def test_checkpoint_contains_completed_epoch_and_history(self) -> None:
        model, optimizer = build_training_objects()
        torch.manual_seed(99)
        state = train_until(model, optimizer, TrainingState(0, ()), INTERRUPT_EPOCH)
        self.assertEqual(state.epoch, INTERRUPT_EPOCH)
        self.assertEqual(len(state.history), INTERRUPT_EPOCH)
        self.assertTrue(all(value > 0 for value in state.history))

    def test_atomic_save_returns_digest_for_written_file(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "checkpoint.pt"
            model, optimizer = build_training_objects()
            digest = save_checkpoint(path, model, optimizer, TrainingState(0, ()))
            self.assertTrue(path.is_file())
            self.assertEqual(digest, file_sha256(path))
            self.assertEqual(len(digest), 64)
            self.assertEqual(list(Path(directory).glob("*.tmp")), [])

    def test_load_restores_model_optimizer_epoch_history_and_rng(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "checkpoint.pt"
            model, optimizer = build_training_objects()
            torch.manual_seed(101)
            state = train_until(model, optimizer, TrainingState(0, ()), INTERRUPT_EPOCH)
            digest = save_checkpoint(path, model, optimizer, state)
            saved_rng = torch.get_rng_state().clone()
            _ = torch.rand(11)
            loaded_model, loaded_optimizer, loaded_state = load_checkpoint(path, digest)
            self.assertEqual(loaded_state, state)
            self.assertTrue(torch.equal(torch.get_rng_state(), saved_rng))
            self.assertTrue(all(
                torch.equal(left, right)
                for left, right in zip(model.parameters(), loaded_model.parameters())
            ))
            self.assertTrue(loaded_optimizer.state_dict()["state"])

    def test_resumed_history_matches_uninterrupted_history_exactly(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            evidence = compare_continuous_and_resumed(Path(directory))
        self.assertEqual(evidence.final_epoch, TOTAL_EPOCHS)
        self.assertEqual(evidence.continuous_history, evidence.resumed_history)

    def test_resumed_model_and_optimizer_match_uninterrupted_run(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            evidence = compare_continuous_and_resumed(Path(directory))
        self.assertTrue(evidence.model_equal)
        self.assertTrue(evidence.optimizer_equal)
        self.assertTrue(evidence.rng_equal_at_load)

    def test_corrupt_checkpoint_is_rejected_before_torch_load(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "checkpoint.pt"
            model, optimizer = build_training_objects()
            digest = save_checkpoint(path, model, optimizer, TrainingState(0, ()))
            with path.open("ab") as handle:
                handle.write(b"tampered")
            with self.assertRaisesRegex(ValueError, "digest mismatch"):
                load_checkpoint(path, digest)

    def test_incompatible_checkpoint_version_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "checkpoint.pt"
            torch.save({"checkpoint_version": 999}, path)
            digest = file_sha256(path)
            with self.assertRaisesRegex(ValueError, "unsupported checkpoint version"):
                load_checkpoint(path, digest)

    def test_fixed_report_is_deterministic_and_states_trust_boundary(self) -> None:
        report = fixed_report()
        self.assertEqual(report, fixed_report())
        self.assertIn("equivalence=history:true,model:true,optimizer:true", report)
        self.assertIn("load=map_location:cpu,weights_only:true,schema:validated", report)
        self.assertTrue(report.endswith(
            "invariants=atomic-write,trusted-local-artifact,exact-resume,no-test-data"
        ))


if __name__ == "__main__":
    unittest.main()
