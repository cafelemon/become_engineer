from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeAlias, TypeVar


P = ParamSpec("P")
R = TypeVar("R")
EventSink: TypeAlias = Callable[[str], None]


def trace_calls(
    event_sink: EventSink,
) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Return a decorator that records deterministic call events."""

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

