from fastapi import Cookie, FastAPI, Header, HTTPException, Response
from auth_lab import AuthService

SESSION_COOKIE = "learning_session"
auth = AuthService()
app = FastAPI(title="Learning dashboard v0.10", version="0.10.0")

@app.post("/api/auth/login")
def login(payload: dict[str, str], response: Response):
    result = auth.login(payload.get("username", ""), payload.get("password", ""))
    if result is None: raise HTTPException(401, "用户名或密码错误", headers={"WWW-Authenticate": "Session"})
    token, csrf = result
    response.set_cookie(SESSION_COOKIE, token, httponly=True, samesite="lax", secure=False, max_age=1800)
    return {"csrf_token": csrf, "user_id": "u-learner"}

@app.get("/api/me")
def me(learning_session: str | None = Cookie(default=None)):
    user_id = auth.authenticate(learning_session)
    if user_id is None: raise HTTPException(401, "需要登录", headers={"WWW-Authenticate": "Session"})
    return {"user_id": user_id}

@app.post("/api/auth/logout", status_code=204)
def logout(response: Response, learning_session: str | None = Cookie(default=None), csrf: str | None = Header(default=None, alias="X-CSRF-Token")):
    if auth.authenticate(learning_session, csrf, unsafe=True) is None: raise HTTPException(403, "CSRF 令牌缺失或无效")
    auth.logout(learning_session); response.delete_cookie(SESSION_COOKIE, httponly=True, samesite="lax")
