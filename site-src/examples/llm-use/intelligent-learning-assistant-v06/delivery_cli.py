from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
import sys
from typing import Any, Mapping, Protocol
from urllib import error, request
import uuid


SENSITIVE_KEYS = frozenset({
    "authorization", "api_key", "apikey", "cookie", "password",
    "secret", "session", "token",
})


class DeliveryError(RuntimeError):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code


@dataclass(frozen=True)
class ProviderConfig:
    mode: str
    provider: str
    model: str
    base_url: str | None
    timeout_seconds: int


@dataclass(frozen=True)
class InvocationResult:
    status: str
    text: str | None
    request_id: str


class Transport(Protocol):
    def post_json(
        self,
        url: str,
        headers: Mapping[str, str],
        payload: Mapping[str, Any],
        timeout_seconds: int,
    ) -> Mapping[str, Any]: ...


class UrllibTransport:
    def post_json(
        self,
        url: str,
        headers: Mapping[str, str],
        payload: Mapping[str, Any],
        timeout_seconds: int,
    ) -> Mapping[str, Any]:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        http_request = request.Request(url, data=body, headers=dict(headers), method="POST")
        try:
            with request.urlopen(http_request, timeout=timeout_seconds) as response:
                decoded = json.loads(response.read().decode("utf-8"))
        except (error.HTTPError, error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            raise DeliveryError("provider_call_failed", "provider call failed") from exc
        if not isinstance(decoded, dict):
            raise DeliveryError("provider_response_invalid", "provider response must be an object")
        return decoded


class ScriptedTransport:
    def __init__(self, response: Mapping[str, Any] | None = None, fail: bool = False) -> None:
        self.response = response or {
            "status": "completed",
            "output_text": "离线验收完成",
            "request_id": "req-scripted",
        }
        self.fail = fail
        self.calls: list[dict[str, Any]] = []

    def post_json(
        self,
        url: str,
        headers: Mapping[str, str],
        payload: Mapping[str, Any],
        timeout_seconds: int,
    ) -> Mapping[str, Any]:
        self.calls.append({
            "url": url,
            "headers": dict(headers),
            "payload": dict(payload),
            "timeout_seconds": timeout_seconds,
        })
        if self.fail:
            raise RuntimeError(f"simulated failure with header {headers.get('Authorization')}")
        return self.response


def load_config(environ: Mapping[str, str]) -> ProviderConfig:
    mode = environ.get("MODEL_MODE", "offline")
    if mode not in {"offline", "provider"}:
        raise DeliveryError("invalid_config", "MODEL_MODE must be offline or provider")
    provider = environ.get("MODEL_PROVIDER", "scripted" if mode == "offline" else "").strip()
    model = environ.get("MODEL_NAME", "learning-assistant-offline").strip()
    raw_timeout = environ.get("MODEL_TIMEOUT_SECONDS", "10")
    try:
        timeout = int(raw_timeout)
    except ValueError as exc:
        raise DeliveryError("invalid_config", "MODEL_TIMEOUT_SECONDS must be an integer") from exc
    if not 1 <= timeout <= 120 or not provider or not model:
        raise DeliveryError("invalid_config", "provider, model and timeout must be valid")

    base_url = environ.get("MODEL_BASE_URL")
    if mode == "provider":
        if not base_url or not base_url.startswith("https://"):
            raise DeliveryError("invalid_config", "provider mode requires an HTTPS base URL")
        if not environ.get("MODEL_API_KEY"):
            raise DeliveryError("missing_secret", "MODEL_API_KEY is required in provider mode")
    return ProviderConfig(mode, provider, model, base_url, timeout)


def require_real_call_opt_in(environ: Mapping[str, str], cli_real: bool) -> None:
    if not cli_real or environ.get("ALLOW_REAL_PROVIDER") != "1":
        raise DeliveryError(
            "real_call_not_enabled",
            "real call requires both --real and ALLOW_REAL_PROVIDER=1",
        )


def _normalize_response(payload: Mapping[str, Any]) -> InvocationResult:
    status = payload.get("status")
    text = payload.get("output_text")
    request_id = payload.get("request_id")
    if status not in {"completed", "refused", "incomplete"}:
        raise DeliveryError("provider_response_invalid", "provider status is invalid")
    if not isinstance(request_id, str) or not request_id:
        raise DeliveryError("provider_response_invalid", "provider request_id is invalid")
    if status == "completed":
        if not isinstance(text, str) or not text:
            raise DeliveryError("provider_response_invalid", "completed response needs text")
    elif text is not None:
        raise DeliveryError("provider_response_invalid", "non-completed response has no text")
    return InvocationResult(status, text, request_id)


def invoke_provider(
    config: ProviderConfig,
    environ: Mapping[str, str],
    prompt: str,
    transport: Transport,
) -> InvocationResult:
    if config.mode != "provider" or not config.base_url:
        raise DeliveryError("wrong_mode", "provider invocation requires provider mode")
    if not prompt.strip():
        raise DeliveryError("invalid_request", "prompt must not be empty")
    api_key = environ.get("MODEL_API_KEY")
    if not api_key:
        raise DeliveryError("missing_secret", "MODEL_API_KEY is required")
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "X-Request-ID": f"req-{uuid.uuid4().hex}",
    }
    payload = {"model": config.model, "input": prompt}
    try:
        response = transport.post_json(
            config.base_url, headers, payload, config.timeout_seconds
        )
    except DeliveryError:
        raise
    except Exception:
        # Do not preserve a third-party exception chain: it may contain headers.
        raise DeliveryError("provider_call_failed", "provider call failed") from None
    return _normalize_response(response)


def redact(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            str(key): "[REDACTED]" if str(key).lower() in SENSITIVE_KEYS else redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [redact(item) for item in value]
    if isinstance(value, tuple):
        return tuple(redact(item) for item in value)
    return value


def audit_event(
    config: ProviderConfig,
    result: InvocationResult,
    attempt: int,
) -> dict[str, Any]:
    return {
        "event": "model_invocation",
        "provider": config.provider,
        "model": config.model,
        "request_id": result.request_id,
        "status": result.status,
        "attempt": attempt,
    }


def offline_evidence() -> str:
    config = load_config({})
    transport = ScriptedTransport()
    provider_config = ProviderConfig(
        "provider", "scripted", "learning-assistant-offline",
        "https://provider.invalid/v1/responses", 10,
    )
    result = invoke_provider(
        provider_config,
        {"MODEL_API_KEY": "synthetic-test-secret"},
        "生成学习计划",
        transport,
    )
    redacted_call = redact(transport.calls[0])
    evidence = [
        "runtime=python:3.11+,dependencies:stdlib-only,network:disabled-by-default",
        f"default=mode:{config.mode},provider:{config.provider},key-required:false",
        f"scripted=status:{result.status},request_id:{result.request_id},calls:{len(transport.calls)}",
        f"audit={json.dumps(audit_event(provider_config, result, 1), ensure_ascii=False, sort_keys=True, separators=(',', ':'))}",
        f"redaction=authorization:{redacted_call['headers']['Authorization']},prompt-logged:false,response-logged:false",
        "real-call=gates:--real+ALLOW_REAL_PROVIDER=1,base-url:https,key:environment-only,ci:false",
        "secret-boundary=process-memory:yes,config-repr:false,audit:false,evidence:false,source-control:false",
        "delivery=offline-evidence:required,real-provider:optional,production-http-client:not-claimed",
        "invariants=offline-default,fail-closed-config,redacted-observability,no-rag,no-tools",
    ]
    return "\n".join(evidence)


def main(argv: list[str] | None = None, environ: Mapping[str, str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Intelligent learning assistant delivery lab")
    parser.add_argument("--real", action="store_true", help="explicitly allow provider call")
    parser.add_argument("--prompt", default="生成一份学习计划")
    args = parser.parse_args(argv)
    current_environ = os.environ if environ is None else environ
    if not args.real:
        print(offline_evidence())
        return 0
    try:
        require_real_call_opt_in(current_environ, args.real)
        config = load_config(current_environ)
        result = invoke_provider(config, current_environ, args.prompt, UrllibTransport())
        print(json.dumps(audit_event(config, result, 1), ensure_ascii=False, sort_keys=True))
        return 0
    except DeliveryError as exc:
        print(json.dumps({"error": exc.code}, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
