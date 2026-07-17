from __future__ import annotations

import os
from typing import Any


DEFAULT_BASE_URL = "https://api.deepseek.com"
DEFAULT_MODEL = "deepseek-v4-pro"


class DeepSeekConfigurationError(RuntimeError):
    """本机配置不足，离线示例仍可继续运行。"""


def _client() -> tuple[Any, str]:
    api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        raise DeepSeekConfigurationError("请先在本机设置 DEEPSEEK_API_KEY")
    try:
        from openai import OpenAI
    except ImportError as exc:
        raise DeepSeekConfigurationError(
            "请先安装 requirements-deepseek.txt 中的可选依赖"
        ) from exc
    base_url = os.environ.get("DEEPSEEK_BASE_URL", DEFAULT_BASE_URL).strip()
    model = os.environ.get("DEEPSEEK_MODEL", DEFAULT_MODEL).strip()
    if not base_url.startswith("https://"):
        raise DeepSeekConfigurationError("DEEPSEEK_BASE_URL 必须使用 https")
    if not model:
        raise DeepSeekConfigurationError("DEEPSEEK_MODEL 不能为空")
    return OpenAI(api_key=api_key, base_url=base_url, timeout=30.0, max_retries=1), model


def _create_completion(client: Any, **kwargs: Any) -> Any:
    """Call DeepSeek without leaking request or response content in failures."""
    try:
        return client.chat.completions.create(**kwargs)
    except Exception as exc:
        if exc.__class__.__module__.startswith(("openai", "httpx", "httpcore")):
            raise RuntimeError(f"DeepSeek 调用失败：{exc.__class__.__name__}") from exc
        raise


def request_json(system_prompt: str, user_prompt: str) -> str:
    client, model = _client()
    response = _create_completion(
        client,
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        stream=False,
        max_tokens=500,
    )
    return response.choices[0].message.content or ""


def request_tool_call(
    messages: list[dict[str, Any]], tools: list[dict[str, Any]]
) -> tuple[dict[str, Any], Any, str]:
    client, model = _client()
    response = _create_completion(
        client,
        model=model,
        messages=messages,
        tools=tools,
        tool_choice="auto",
        stream=False,
        max_tokens=500,
    )
    message = response.choices[0].message
    calls = message.tool_calls or []
    if len(calls) != 1:
        raise RuntimeError("模型必须提出且只能提出一次工具调用")
    call = calls[0]
    return {
        "id": call.id,
        "name": call.function.name,
        "arguments": call.function.arguments,
    }, message, model


def request_final_answer(
    messages: list[dict[str, Any]], model_message: Any, call_id: str, tool_output: str
) -> str:
    client, model = _client()
    continued = list(messages)
    continued.append(model_message.model_dump(exclude_none=True))
    continued.append({"role": "tool", "tool_call_id": call_id, "content": tool_output})
    response = _create_completion(
        client,
        model=model,
        messages=continued,
        stream=False,
        max_tokens=500,
    )
    return response.choices[0].message.content or ""
