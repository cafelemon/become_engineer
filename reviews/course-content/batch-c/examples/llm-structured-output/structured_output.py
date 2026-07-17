from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError


EXAMPLES = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(EXAMPLES))

from shared.deepseek_client import request_json  # noqa: E402


class LearningRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    goal: Literal["interest", "job"]
    topic: str = Field(min_length=1, max_length=60)
    weekly_hours: int = Field(ge=1, le=40)
    current_level: Literal["beginner", "basic"]


FIXTURES = {
    "valid": '{"goal":"job","topic":"Python","weekly_hours":8,"current_level":"beginner"}',
    "invalid-json": '{"goal":"job","topic":"Python",}',
    "wrong-type": '{"goal":"job","topic":"Python","weekly_hours":"很多","current_level":"beginner"}',
    "extra-field": '{"goal":"job","topic":"Python","weekly_hours":8,"current_level":"beginner","phone":"13800000000"}',
    "missing-field": '{"goal":"job","topic":"Python","weekly_hours":8}',
    "empty": "",
}


SYSTEM_PROMPT = """你负责把学习需求整理成 JSON。只输出一个 JSON 对象，不要补充说明。
字段必须是 goal、topic、weekly_hours、current_level。
goal 只能是 interest 或 job；current_level 只能是 beginner 或 basic；weekly_hours 是 1 到 40 的整数。
示例 JSON：{"goal":"job","topic":"Python","weekly_hours":8,"current_level":"beginner"}
信息不足时也不要猜测，返回缺少字段的 JSON，让应用负责拒绝。"""


def parse_learning_request(content: str) -> LearningRequest:
    if not content.strip():
        raise ValueError("模型没有返回内容")
    try:
        payload = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError("模型返回的内容不是合法 JSON") from exc
    if not isinstance(payload, dict):
        raise ValueError("模型必须返回一个 JSON 对象")
    try:
        return LearningRequest.model_validate(payload)
    except ValidationError as exc:
        raise ValueError("JSON 字段没有通过 LearningRequest 校验") from exc


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--case", choices=sorted(FIXTURES), default="valid")
    parser.add_argument("--use-deepseek", action="store_true")
    parser.add_argument(
        "--prompt",
        default="我想转行学 Python，每周能学 8 小时，目前刚起步。",
    )
    args = parser.parse_args()
    try:
        content = request_json(SYSTEM_PROMPT, args.prompt) if args.use_deepseek else FIXTURES[args.case]
        request = parse_learning_request(content)
    except (ValueError, RuntimeError) as exc:
        print(f"拒绝：{exc}")
        raise SystemExit(1) from exc
    print(request.model_dump_json(indent=2))


if __name__ == "__main__":
    main()
