"""Opaque server-side sessions: no JWT and no raw session value at rest."""
from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


@dataclass
class Session:
    user_id: str
    token_digest: str
    csrf_digest: str
    expires_at: datetime
    revoked: bool = False


class AuthService:
    def __init__(self) -> None:
        self._users = {"learner": ("u-learner", password_hash.hash("learning-only-password"))}
        self._sessions: dict[str, Session] = {}

    def login(self, username: str, password: str) -> tuple[str, str] | None:
        row = self._users.get(username)
        if row is None or not password_hash.verify(password, row[1]):
            return None
        token, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(24)
        self._sessions[digest(token)] = Session(row[0], digest(token), digest(csrf), datetime.now(UTC) + timedelta(minutes=30))
        return token, csrf

    def authenticate(self, token: str | None, csrf: str | None = None, unsafe: bool = False) -> str | None:
        if not token:
            return None
        session = self._sessions.get(digest(token))
        if session is None or session.revoked or session.expires_at <= datetime.now(UTC):
            return None
        if unsafe and (not csrf or not secrets.compare_digest(session.csrf_digest, digest(csrf))):
            return None
        return session.user_id

    def logout(self, token: str | None) -> None:
        if token and (session := self._sessions.get(digest(token))):
            session.revoked = True

    def expire(self, token: str) -> None:
        """Test-only clock control without sleeping."""
        self._sessions[digest(token)].expires_at = datetime.now(UTC) - timedelta(seconds=1)
