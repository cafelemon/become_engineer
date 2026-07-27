"""Browser-test application backed by the migrated PostgreSQL schema."""
from __future__ import annotations

import hashlib
import os
import secrets
import uuid
from contextlib import asynccontextmanager
from datetime import UTC, datetime, timedelta
from pathlib import Path

from fastapi import Cookie, FastAPI, Header, HTTPException, Response
from fastapi.responses import FileResponse, HTMLResponse
from pwdlib import PasswordHash
from sqlalchemy import create_engine, text

ROOT = Path(__file__).resolve().parent
DATABASE_URL = os.environ.get(
    "WEB_ENGINEERING_DATABASE_URL",
    "postgresql+psycopg://dashboard:dashboard@127.0.0.1:55439/dashboard",
)
SESSION_COOKIE = "learning_session"
password_hash = PasswordHash.recommended()
engine = create_engine(DATABASE_URL, pool_pre_ping=True)


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def seed_synthetic_user() -> None:
    with engine.begin() as connection:
        connection.execute(
            text(
                """INSERT INTO users(user_id, username, password_hash, role)
                   VALUES (:user_id, :username, :password_hash, 'learner')
                   ON CONFLICT (username) DO UPDATE SET password_hash = EXCLUDED.password_hash"""
            ),
            {
                "user_id": "u-browser-learner",
                "username": "browser-learner",
                "password_hash": password_hash.hash("learning-only-password"),
            },
        )
        connection.execute(
            text(
                """INSERT INTO learners(learner_id, name, description, owner_user_id)
                   VALUES ('browser-learner', '浏览器学习者', '合成 E2E 数据', 'u-browser-learner')
                   ON CONFLICT (learner_id) DO UPDATE SET owner_user_id = EXCLUDED.owner_user_id"""
            )
        )


@asynccontextmanager
async def lifespan(_: FastAPI):
    seed_synthetic_user()
    yield
    engine.dispose()


app = FastAPI(title="Learning dashboard v0.12 E2E", lifespan=lifespan)


def session_row(token: str | None):
    if not token:
        return None
    with engine.connect() as connection:
        return connection.execute(
            text(
                """SELECT s.session_id, s.user_id, s.csrf_digest, u.role
                   FROM auth_sessions s JOIN users u ON u.user_id = s.user_id
                   WHERE s.token_digest = :digest AND s.revoked_at IS NULL
                     AND s.expires_at > CURRENT_TIMESTAMP"""
            ),
            {"digest": digest(token)},
        ).mappings().first()


def require_session(token: str | None):
    row = session_row(token)
    if row is None:
        raise HTTPException(401, "需要登录", headers={"WWW-Authenticate": "Session"})
    return row


def require_csrf(row, csrf: str | None) -> None:
    if not csrf or not secrets.compare_digest(row["csrf_digest"], digest(csrf)):
        raise HTTPException(403, "CSRF 令牌缺失或无效")


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    return """<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>学习进度报告器 v0.12</title><style>
:root{color-scheme:light dark;font-family:system-ui,sans-serif}body{max-width:46rem;margin:2rem auto;padding:0 1rem}
form,.panel{display:grid;gap:.75rem;padding:1rem;border:1px solid #777;border-radius:.75rem}input,button{font:inherit;padding:.65rem}
[hidden]{display:none}.error{border-left:.3rem solid #b00020;padding:.6rem}.ok{color:#087830}@media(max-width:390px){body{margin:1rem auto}}
@media(prefers-reduced-motion:reduce){*{scroll-behavior:auto!important;transition:none!important}}
</style></head><body><main>
<h1>学习进度报告器</h1><p id="restoring" role="status">正在从服务端恢复身份…</p>
<form id="login" hidden><h2>登录</h2><label>用户名 <input name="username" value="browser-learner" autocomplete="username"></label>
<label>密码 <input name="password" value="learning-only-password" type="password" autocomplete="current-password"></label>
<button>登录</button><p id="login-error" class="error" role="alert" tabindex="-1" hidden></p></form>
<section id="dashboard" class="panel" hidden><h2>学习看板</h2><p id="identity"></p>
<label>学习记录 <input id="note" value="Playwright 写入"></label><button id="save">保存记录</button>
<button id="diagnostic">运行操作员诊断</button><p id="result" role="status"></p><button id="logout">退出</button></section>
</main><script type="module" src="/assets/e2e.js"></script></body></html>"""


@app.get("/assets/e2e.js")
def compiled_frontend() -> FileResponse:
    return FileResponse(ROOT / "dist" / "e2e.js", media_type="text/javascript")


@app.post("/api/auth/login")
def login(payload: dict[str, str], response: Response):
    with engine.connect() as connection:
        user = connection.execute(
            text("SELECT user_id, password_hash FROM users WHERE username = :username"),
            {"username": payload.get("username", "")},
        ).mappings().first()
    if user is None or not password_hash.verify(payload.get("password", ""), user["password_hash"]):
        raise HTTPException(401, "用户名或密码错误", headers={"WWW-Authenticate": "Session"})
    token, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(24)
    with engine.begin() as connection:
        connection.execute(
            text(
                """INSERT INTO auth_sessions(session_id, user_id, token_digest, csrf_digest, expires_at)
                   VALUES (:session_id, :user_id, :token_digest, :csrf_digest, :expires_at)"""
            ),
            {
                "session_id": str(uuid.uuid4()),
                "user_id": user["user_id"],
                "token_digest": digest(token),
                "csrf_digest": digest(csrf),
                "expires_at": datetime.now(UTC) + timedelta(minutes=30),
            },
        )
    response.set_cookie(SESSION_COOKIE, token, httponly=True, samesite="lax", secure=False, max_age=1800)
    return {"user_id": user["user_id"], "csrf_token": csrf}


@app.get("/api/me")
def me(learning_session: str | None = Cookie(default=None)):
    row = require_session(learning_session)
    csrf = secrets.token_urlsafe(24)
    with engine.begin() as connection:
        connection.execute(
            text("UPDATE auth_sessions SET csrf_digest = :csrf WHERE session_id = :session_id"),
            {"csrf": digest(csrf), "session_id": row["session_id"]},
        )
    return {"user_id": row["user_id"], "csrf_token": csrf}


@app.post("/api/study")
def save_study(
    payload: dict[str, str],
    learning_session: str | None = Cookie(default=None),
    csrf: str | None = Header(default=None, alias="X-CSRF-Token"),
):
    row = require_session(learning_session)
    require_csrf(row, csrf)
    with engine.begin() as connection:
        learner_id = connection.scalar(
            text("SELECT learner_id FROM learners WHERE owner_user_id = :user_id"),
            {"user_id": row["user_id"]},
        )
        if learner_id is None:
            raise HTTPException(404, "资源不可见")
        connection.execute(
            text(
                """INSERT INTO study_sessions(learner_id, hours, note, idempotency_key)
                   VALUES (:learner_id, 0.25, :note, :key)"""
            ),
            {"learner_id": learner_id, "note": payload.get("note", ""), "key": str(uuid.uuid4())},
        )
    return {"saved": True, "note": payload.get("note", "")}


@app.post("/api/operator/diagnostic")
def diagnostic(
    learning_session: str | None = Cookie(default=None),
    csrf: str | None = Header(default=None, alias="X-CSRF-Token"),
):
    row = require_session(learning_session)
    require_csrf(row, csrf)
    if row["role"] != "operator":
        raise HTTPException(403, "当前角色没有诊断权限")
    return {"status": "ok"}


@app.post("/api/auth/logout", status_code=204)
def logout(
    response: Response,
    learning_session: str | None = Cookie(default=None),
    csrf: str | None = Header(default=None, alias="X-CSRF-Token"),
):
    row = require_session(learning_session)
    require_csrf(row, csrf)
    with engine.begin() as connection:
        connection.execute(
            text("UPDATE auth_sessions SET revoked_at = CURRENT_TIMESTAMP WHERE session_id = :session_id"),
            {"session_id": row["session_id"]},
        )
    response.delete_cookie(SESSION_COOKIE, httponly=True, samesite="lax")
