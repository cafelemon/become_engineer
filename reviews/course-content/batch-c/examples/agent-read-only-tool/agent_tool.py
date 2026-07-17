from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any


EXAMPLES = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EXAMPLES))

from shared.deepseek_client import request_final_answer, request_tool_call  # noqa: E402


CATALOG_PATH = Path(__file__).with_name("data") / "course_catalog.json"
COURSE_ID = re.compile(r"^[a-z0-9][a-z0-9-]{2,63}$")
TOOL_NAME = "get_course_summary"
TOOLS = [{
    "type": "function",
    "function": {
        "name": TOOL_NAME,
        "description": "按固定课程 ID 查询公开课程的标题、状态、前置和 URL",
        "parameters": {
            "type": "object",
            "properties": {"course_id": {"type": "string"}},
            "required": ["course_id"],
            "additionalProperties": False,
        },
    },
}]


class ToolCallError(ValueError):
    pass


def load_catalog(path: Path = CATALOG_PATH) -> dict[str, dict[str, Any]]:
    rows = json.loads(path.read_text(encoding="utf-8"))
    return {row["course_id"]: row for row in rows}


def execute_tool(name: str, arguments: str, catalog: dict[str, dict[str, Any]]) -> dict[str, Any]:
    if name != TOOL_NAME:
        raise ToolCallError("这个工具没有注册")
    try:
        payload = json.loads(arguments)
    except json.JSONDecodeError as exc:
        raise ToolCallError("工具参数不是合法 JSON") from exc
    if not isinstance(payload, dict) or set(payload) != {"course_id"}:
        raise ToolCallError("工具只接受 course_id 一个字段")
    course_id = payload["course_id"]
    if not isinstance(course_id, str) or not COURSE_ID.fullmatch(course_id):
        raise ToolCallError("course_id 格式不正确")
    course = catalog.get(course_id)
    if course is None:
        raise ToolCallError("没有找到这门课程")
    return course


def offline_run(course_id: str) -> dict[str, Any]:
    call = {"id": "call_offline_001", "name": TOOL_NAME, "arguments": json.dumps({"course_id": course_id})}
    result = execute_tool(call["name"], call["arguments"], load_catalog())
    return {"tool_call": call, "tool_result": result, "answer": f"找到课程《{result['title']}》，状态：{result['status']}。"}


def deepseek_run(prompt: str) -> dict[str, Any]:
    messages: list[dict[str, Any]] = [
        {
            "role": "system",
            "content": (
                "你是学习路线助手，但你不知道课程目录的实时内容。"
                "用户查询课程信息时，必须先调用已注册的 get_course_summary 工具；"
                "不得凭记忆回答，也不得编造课程 ID。"
            ),
        },
        {"role": "user", "content": prompt},
    ]
    call, model_message, _model = request_tool_call(messages, TOOLS)
    result = execute_tool(call["name"], call["arguments"], load_catalog())
    result_text = json.dumps(result, ensure_ascii=False)
    answer = request_final_answer(messages, model_message, call["id"], result_text)
    return {"tool_call": call, "tool_result": result, "answer": answer}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--course-id", default="python-basics-01")
    parser.add_argument("--use-deepseek", action="store_true")
    parser.add_argument(
        "--prompt",
        default="请调用课程查询工具，查询 course_id 为 python-basics-01 的课程状态。",
    )
    args = parser.parse_args()
    try:
        trace = deepseek_run(args.prompt) if args.use_deepseek else offline_run(args.course_id)
    except (ToolCallError, RuntimeError) as exc:
        print(f"拒绝：{exc}")
        raise SystemExit(1) from exc
    print(json.dumps(trace, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
