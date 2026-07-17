from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path
import random

from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler


SEED = 42
FIELDNAMES = [
    "planned_hours", "completed_hours", "practice_runs", "blocked_minutes", "goal_met"
]


@dataclass(frozen=True)
class ExperimentResult:
    rows: int
    baseline_accuracy: float
    model_accuracy: float
    matrix: list[list[int]]
    mistakes: int


def generate_rows(count: int = 240, seed: int = SEED) -> list[dict[str, float | int]]:
    rng = random.Random(seed)
    rows: list[dict[str, float | int]] = []
    for _ in range(count):
        planned = rng.randint(2, 14)
        completed = round(max(0.0, min(16.0, rng.gauss(planned * 0.72, 2.4))), 1)
        practice = rng.randint(0, 8)
        blocked = rng.randrange(0, 181, 10)
        noise = rng.uniform(-1.8, 1.8)
        score = completed - planned * 0.68 + practice * 0.38 - blocked / 95 + noise
        rows.append({
            "planned_hours": planned,
            "completed_hours": completed,
            "practice_runs": practice,
            "blocked_minutes": blocked,
            "goal_met": int(score >= 0),
        })
    return rows


def write_csv(path: Path, rows: list[dict[str, float | int]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def run_experiment(rows: list[dict[str, float | int]]) -> ExperimentResult:
    features = [
        [row["planned_hours"], row["completed_hours"], row["practice_runs"], row["blocked_minutes"]]
        for row in rows
    ]
    labels = [int(row["goal_met"]) for row in rows]
    x_train, x_valid, y_train, y_valid = train_test_split(
        features, labels, test_size=0.25, random_state=SEED, stratify=labels
    )
    baseline = DummyClassifier(strategy="most_frequent")
    baseline.fit(x_train, y_train)
    model = make_pipeline(StandardScaler(), LogisticRegression(random_state=SEED))
    model.fit(x_train, y_train)
    baseline_prediction = baseline.predict(x_valid)
    prediction = model.predict(x_valid)
    matrix = confusion_matrix(y_valid, prediction, labels=[0, 1]).tolist()
    return ExperimentResult(
        rows=len(rows),
        baseline_accuracy=float(accuracy_score(y_valid, baseline_prediction)),
        model_accuracy=float(accuracy_score(y_valid, prediction)),
        matrix=matrix,
        mistakes=sum(int(left != right) for left, right in zip(y_valid, prediction, strict=True)),
    )


def main() -> None:
    rows = generate_rows()
    output = Path(__file__).with_name("synthetic_study_sessions.csv")
    write_csv(output, rows)
    result = run_experiment(rows)
    print("数据：教学合成学习记录（不代表真实学习者）")
    print(f"记录数：{result.rows}")
    print(f"多数类基线：{result.baseline_accuracy:.3f}")
    print(f"逻辑回归：{result.model_accuracy:.3f}")
    print(f"混淆矩阵：{result.matrix}")
    print(f"验证集错例：{result.mistakes}")


if __name__ == "__main__":
    main()
