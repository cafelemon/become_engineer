"""Contract tests for the v0.2 teaching experiment."""

import unittest

import experiment


class ExperimentTests(unittest.TestCase):
    def test_character_pairs_and_idf(self):
        self.assertEqual(experiment.tokens("A 中 文"), ["a中", "中文"])
        idf = experiment.fit_vectorizer(["甲乙", "甲乙", "乙丙"])
        self.assertAlmostEqual(idf["甲乙"], 1 + __import__("math").log(4 / 3))
        self.assertEqual(experiment.transform("未知", idf), {})

    def test_vector_has_unit_norm(self):
        idf = experiment.fit_vectorizer(["学习计划", "代码错误"])
        vector = experiment.transform("学习计划", idf)
        self.assertAlmostEqual(sum(value * value for value in vector.values()), 1)

    def test_only_train_text_controls_vocabulary(self):
        v01 = experiment.load_v01()
        partitions = v01.split_rows(v01.read_corpus())
        idf = experiment.fit_vectorizer([row["text"] for row in partitions["train"]])
        changed = {name: [dict(row) for row in part] for name, part in partitions.items()}
        changed["validation"][0]["text"] = "仅验证集才有的特异新词"
        changed["test"][0]["text"] = "密封测试集唯一词"
        other = experiment.fit_vectorizer([row["text"] for row in changed["train"]])
        self.assertEqual(idf, other)

    def test_split_and_validation_contract_are_reused(self):
        report = experiment.run()
        self.assertEqual(len(report["train_ids"]), 24)
        self.assertEqual(len(report["validation_ids"]), 8)
        self.assertTrue(set(report["train_ids"]).isdisjoint(report["validation_ids"]))
        self.assertEqual(report["baseline_validation"]["accuracy"], 0.5)
        self.assertEqual(report["model_validation"]["accuracy"], 0.875)
        self.assertEqual([item["sample_id"] for item in report["validation_errors"]], ["P09"])
        self.assertEqual(report["vocabulary_size"], 232)
        self.assertNotIn("test_ids", report)

    def test_training_is_deterministic(self):
        self.assertEqual(experiment.run(), experiment.run())

    def test_invalid_training_configuration_fails(self):
        with self.assertRaises(ValueError):
            experiment.train_linear([], {"甲乙": 1.0})


if __name__ == "__main__":
    unittest.main()
