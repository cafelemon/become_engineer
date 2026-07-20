from __future__ import annotations

import hashlib
import hmac
import secrets
from dataclasses import dataclass


STATUS_READ = "status:read"
DIAGNOSTIC_RUN = "diagnostic:run"


@dataclass(frozen=True)
class Principal:
    principal_id: str
    scopes: frozenset[str]


@dataclass(frozen=True)
class Response:
    status: int
    headers: dict[str, str]
    body: dict[str, str]


class TokenStore:
    def __init__(self) -> None:
        self._principals_by_digest: dict[str, Principal] = {}

    @staticmethod
    def _digest(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def issue(self, principal: Principal) -> str:
        token = secrets.token_urlsafe(32)
        self._principals_by_digest[self._digest(token)] = principal
        return token

    def authenticate(self, authorization: str | None) -> Principal | None:
        if authorization is None or not authorization.startswith("Bearer "):
            return None
        token = authorization.removeprefix("Bearer ").strip()
        if not token:
            return None
        candidate = self._digest(token)
        for digest, principal in self._principals_by_digest.items():
            if hmac.compare_digest(candidate, digest):
                return principal
        return None

    def stored_digests(self) -> tuple[str, ...]:
        return tuple(self._principals_by_digest)


class RuntimeObserverApp:
    ROUTES = {
        ("GET", "/status"): STATUS_READ,
        ("POST", "/diagnostics"): DIAGNOSTIC_RUN,
    }

    def __init__(self, tokens: TokenStore) -> None:
        self.tokens = tokens
        self.audit_log: list[str] = []

    def handle(self, method: str, path: str, authorization: str | None) -> Response:
        action = self.ROUTES.get((method, path))
        if action is None:
            self.audit_log.append(
                f"principal=unknown action=unlisted result=404 method={method} path={path}"
            )
            return Response(status=404, headers={}, body={"error": "not_found"})

        principal = self.tokens.authenticate(authorization)
        if principal is None:
            self.audit_log.append(f"principal=anonymous action={action} result=401")
            return Response(
                status=401,
                headers={"WWW-Authenticate": 'Bearer realm="runtime-observer"'},
                body={"error": "authentication_required"},
            )

        if action not in principal.scopes:
            self.audit_log.append(
                f"principal={principal.principal_id} action={action} result=403"
            )
            return Response(
                status=403,
                headers={},
                body={"error": "insufficient_permission"},
            )

        self.audit_log.append(
            f"principal={principal.principal_id} action={action} result=200"
        )
        if action == STATUS_READ:
            body = {"status": "ok"}
        else:
            body = {"diagnostic": "completed"}
        return Response(status=200, headers={}, body=body)


def build_demo() -> tuple[RuntimeObserverApp, str, str]:
    tokens = TokenStore()
    viewer_token = tokens.issue(
        Principal(principal_id="viewer", scopes=frozenset({STATUS_READ}))
    )
    operator_token = tokens.issue(
        Principal(
            principal_id="operator",
            scopes=frozenset({STATUS_READ, DIAGNOSTIC_RUN}),
        )
    )
    return RuntimeObserverApp(tokens), viewer_token, operator_token


def main() -> None:
    app, viewer_token, operator_token = build_demo()
    anonymous = app.handle("GET", "/status", None)
    viewer = app.handle("GET", "/status", f"Bearer {viewer_token}")
    denied = app.handle("POST", "/diagnostics", f"Bearer {viewer_token}")
    operator = app.handle("POST", "/diagnostics", f"Bearer {operator_token}")
    raw_token_logged = any(
        token in line
        for token in (viewer_token, operator_token)
        for line in app.audit_log
    )

    challenge = anonymous.headers["WWW-Authenticate"].split(" ", 1)[0]
    print(f"anonymous: status={anonymous.status} challenge={challenge}")
    print(f"viewer: action={STATUS_READ} status={viewer.status}")
    print(
        "denied: "
        f"principal=viewer action={DIAGNOSTIC_RUN} status={denied.status}"
    )
    print(
        "operator: "
        f"action={DIAGNOSTIC_RUN} status={operator.status}"
    )
    print(f"audit: entries={len(app.audit_log)} raw_token_logged={raw_token_logged}")


if __name__ == "__main__":
    main()
