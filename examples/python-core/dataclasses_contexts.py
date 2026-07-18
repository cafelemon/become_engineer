from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field, replace
from pathlib import Path
from tempfile import TemporaryDirectory


@dataclass
class StudyRecord:
    course_name: str
    target_hours: float
    completed_hours: float
    tags: list[str] = field(default_factory=list)

    @property
    def progress(self) -> float:
        if self.target_hours <= 0.0:
            return 0.0
        raw = self.completed_hours / self.target_hours
        return min(max(raw, 0.0), 1.0)

    @property
    def status(self) -> str:
        return "已完成" if self.completed_hours >= self.target_hours else "进行中"

    def clone(self) -> StudyRecord:
        return replace(self, tags=list(self.tags))

    def add_completed_hours(self, additional_hours: float) -> None:
        if additional_hours < 0.0:
            raise ValueError("增加的小时数不能为负数")
        self.completed_hours += additional_hours


def write_audit_snapshot(
    records: Iterable[StudyRecord], output_path: Path
) -> tuple[bool, bool]:
    snapshot = [record.clone() for record in records]
    output_closed = False
    try:
        with output_path.open("w", encoding="utf-8") as output:
            output.write("学习审计快照\n")
            for record in snapshot:
                output.write(
                    f"{record.course_name}\t{record.target_hours:g}\t"
                    f"{record.completed_hours:g}\n"
                )
        output_closed = output.closed
    except OSError:
        return False, output_closed
    return True, output_closed


def main() -> None:
    original = StudyRecord("Python 起步", 10.0, 7.5, ["基础"])
    print(f"before={original.progress:.1%} {original.status}")
    original.add_completed_hours(2.5)
    print(f"after={original.progress:.1%} {original.status}")

    copied = original.clone()
    copied.tags.append("重点")
    print(f"original_tags={original.tags}")
    print(f"copied_tags={copied.tags}")

    with TemporaryDirectory() as directory:
        root = Path(directory)
        audit_ok, audit_closed = write_audit_snapshot([original], root / "audit.txt")
        missing_ok, _ = write_audit_snapshot(
            [original], root / "missing" / "audit.txt"
        )
        print(f"audit_ok={audit_ok}")
        print(f"audit_closed={audit_closed}")
        print(f"missing_parent={missing_ok}")


if __name__ == "__main__":
    main()
