from __future__ import annotations

import gc
import tempfile
import tracemalloc
import weakref
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Payload:
    data: bytearray


@dataclass(frozen=True)
class MemoryLifecycleResult:
    retained: bool
    released: bool
    traced_drop: bool


@dataclass(frozen=True)
class FileLifecycleResult:
    open_inside: bool
    closed_outside: bool
    read_after_close_error: str


def observe_memory_lifecycle(size: int = 1_000_000) -> MemoryLifecycleResult:
    if size <= 0:
        raise ValueError("size must be positive")

    tracemalloc.start()
    try:
        gc.collect()
        payload = Payload(bytearray(size))
        observer = weakref.ref(payload)
        alias = payload
        del payload

        retained = observer() is not None
        allocated, _ = tracemalloc.get_traced_memory()

        del alias
        gc.collect()
        released = observer() is None
        after_release, _ = tracemalloc.get_traced_memory()
        return MemoryLifecycleResult(
            retained=retained,
            released=released,
            traced_drop=after_release < allocated,
        )
    finally:
        tracemalloc.stop()


def observe_file_lifecycle(path: Path) -> FileLifecycleResult:
    with path.open("w+", encoding="utf-8") as handle:
        handle.write("runtime observer\n")
        handle.seek(0)
        open_inside = not handle.closed and handle.read() == "runtime observer\n"

    try:
        handle.read()
    except ValueError as error:
        read_after_close_error = type(error).__name__
    else:
        read_after_close_error = "none"

    return FileLifecycleResult(
        open_inside=open_inside,
        closed_outside=handle.closed,
        read_after_close_error=read_after_close_error,
    )


def closes_file_after_error(path: Path) -> bool:
    handle = None
    try:
        with path.open("w", encoding="utf-8") as handle:
            handle.write("before failure\n")
            raise RuntimeError("simulated processing failure")
    except RuntimeError:
        return handle is not None and handle.closed


def temporary_directory_is_removed() -> bool:
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory)
        (path / "trace.txt").write_text("temporary\n", encoding="utf-8")
        existed_inside = path.exists()
    return existed_inside and not path.exists()


def main() -> None:
    memory = observe_memory_lifecycle()
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "resource.txt"
        file_result = observe_file_lifecycle(path)
        closed_after_error = closes_file_after_error(path)

    print(
        "memory: "
        f"retained={memory.retained} released={memory.released} "
        f"traced_drop={memory.traced_drop}"
    )
    print(
        "file: "
        f"open_inside={file_result.open_inside} "
        f"closed_outside={file_result.closed_outside}"
    )
    print(f"failure: closed_after_error={closed_after_error}")
    print(f"temporary: removed={temporary_directory_is_removed()}")


if __name__ == "__main__":
    main()
