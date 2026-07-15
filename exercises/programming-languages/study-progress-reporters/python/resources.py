from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path


@contextmanager
def staged_output_path(output_path: Path) -> Iterator[Path]:
    """Yield a sibling temporary path and replace the final file on success."""

    pending_path = output_path.with_name(f".{output_path.name}.tmp")
    try:
        yield pending_path
        pending_path.replace(output_path)
    finally:
        pending_path.unlink(missing_ok=True)
