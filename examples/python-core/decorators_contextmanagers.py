from __future__ import annotations

from collections.abc import Callable, Iterator
from contextlib import contextmanager
from functools import wraps
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import ParamSpec, TypeAlias, TypeVar


P = ParamSpec("P")
R = TypeVar("R")
EventSink: TypeAlias = Callable[[str], None]


def trace_calls(
    event_sink: EventSink,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    def decorate(function: Callable[P, R]) -> Callable[P, R]:
        @wraps(function)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            event_sink(f"开始:{function.__name__}")
            try:
                result = function(*args, **kwargs)
            except Exception as error:
                event_sink(f"失败:{function.__name__}:{type(error).__name__}")
                raise
            event_sink(f"完成:{function.__name__}")
            return result

        return wrapper

    return decorate


@contextmanager
def staged_output_path(output_path: Path) -> Iterator[Path]:
    pending_path = output_path.with_name(f".{output_path.name}.tmp")
    try:
        yield pending_path
        pending_path.replace(output_path)
    finally:
        pending_path.unlink(missing_ok=True)


def main() -> None:
    events: list[str] = []

    @trace_calls(events.append)
    def join_text(left: str, right: str = "!") -> str:
        """Join two pieces of text."""
        return left + right

    print(f"result={join_text('完成', right='。')}")
    print(f"events={events}")
    print(f"name={join_text.__name__}")

    failure_events: list[str] = []

    @trace_calls(failure_events.append)
    def fail_export() -> None:
        raise ValueError("审计数据无效")

    try:
        fail_export()
    except ValueError as error:
        print(f"failure={type(error).__name__}")
    print(f"failure_events={failure_events}")

    with TemporaryDirectory() as directory:
        root = Path(directory)
        output_path = root / "audit.txt"
        with staged_output_path(output_path) as pending_path:
            pending_path.write_text("新审计内容\n", encoding="utf-8")
        print(f"published={output_path.read_text(encoding='utf-8').strip()}")

        output_path.write_text("旧审计内容\n", encoding="utf-8")
        pending_path = output_path.with_name(f".{output_path.name}.tmp")
        try:
            with staged_output_path(output_path) as staged_path:
                staged_path.write_text("未完成内容\n", encoding="utf-8")
                raise RuntimeError("模拟块内失败")
        except RuntimeError:
            pass
        print(f"preserved={output_path.read_text(encoding='utf-8').strip()}")
        print(f"pending_exists={pending_path.exists()}")


if __name__ == "__main__":
    main()
