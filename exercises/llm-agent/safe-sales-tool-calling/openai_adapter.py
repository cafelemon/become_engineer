from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from safe_sales import TOOL_SCHEMA, ToolValidationError, execute_tool_call


def _tool_error(error: Exception) -> dict[str, Any]:
    if isinstance(error, ToolValidationError):
        return {"ok": False, "error": str(error), "error_type": "validation_error"}
    return {
        "ok": False,
        "error": "The tool could not complete the request.",
        "error_type": "tool_error",
    }


def run_with_openai(
    prompt: str,
    db_path: Path,
    *,
    model: str | None = None,
    max_rounds: int = 4,
) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    model = model or os.getenv("OPENAI_MODEL")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is required for --use-openai")
    if not model:
        raise RuntimeError("OPENAI_MODEL is required for --use-openai")

    try:
        from openai import OpenAI
    except ImportError as error:
        raise RuntimeError(
            "Install the optional dependency with "
            "'pip install -r requirements-openai.txt'"
        ) from error

    client = OpenAI(api_key=api_key)
    input_items: list[Any] = [{"role": "user", "content": prompt}]
    tool_rounds = 0

    while True:
        response = client.responses.create(
            model=model,
            instructions=(
                "Use the sales tool for sales questions. "
                "Do not invent sales data. Explain empty results plainly."
            ),
            tools=[TOOL_SCHEMA],
            input=input_items,
        )
        input_items.extend(response.output)
        function_calls = [
            item for item in response.output if item.type == "function_call"
        ]
        if not function_calls:
            return response.output_text
        if tool_rounds >= max_rounds:
            raise RuntimeError(
                f"tool loop exceeded the maximum of {max_rounds} rounds"
            )

        for function_call in function_calls:
            try:
                result = execute_tool_call(
                    db_path,
                    name=function_call.name,
                    arguments=function_call.arguments,
                )
            except Exception as error:
                result = _tool_error(error)

            input_items.append(
                {
                    "type": "function_call_output",
                    "call_id": function_call.call_id,
                    "output": json.dumps(result, ensure_ascii=False),
                }
            )
        tool_rounds += 1
