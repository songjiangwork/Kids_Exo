import secrets
from dataclasses import dataclass, field

from fastapi import APIRouter, HTTPException, Request, Response

from kids_exo.persistence.models import AccountEntity
from kids_exo.persistence.repository import PracticeRepository
from kids_exo.web.dependencies import require_repository
from kids_exo.web.schemas import AccountResponse, AuthMeResponse, LoginRequest


SESSION_COOKIE_NAME = "kids_exo_session"


@dataclass
class LocalSessionStore:
    _sessions: dict[str, int] = field(default_factory=dict)

    def create_session(self, account_id: int) -> str:
        token = secrets.token_urlsafe(32)
        self._sessions[token] = account_id
        return token

    def account_id_for_token(self, token: str | None) -> int | None:
        if token is None:
            return None
        return self._sessions.get(token)

    def delete_session(self, token: str | None) -> None:
        if token is not None:
            self._sessions.pop(token, None)


def create_router(
    repository: PracticeRepository | None,
    session_store: LocalSessionStore | None = None,
) -> APIRouter:
    router = APIRouter()
    sessions = session_store or LocalSessionStore()

    @router.post("/api/auth/login", response_model=AuthMeResponse)
    def login(request: LoginRequest, response: Response) -> AuthMeResponse:
        storage = require_repository(repository)
        try:
            account = storage.verify_account_password(request.email, request.password)
        except ValueError as exc:
            raise HTTPException(status_code=401, detail="Invalid email or password") from exc
        token = sessions.create_session(account.id)
        response.set_cookie(
            SESSION_COOKIE_NAME,
            token,
            httponly=True,
            samesite="lax",
            path="/",
        )
        return AuthMeResponse(account=_account_response(account))

    @router.post("/api/auth/logout", response_model=AuthMeResponse)
    def logout(request: Request, response: Response) -> AuthMeResponse:
        sessions.delete_session(request.cookies.get(SESSION_COOKIE_NAME))
        response.delete_cookie(SESSION_COOKIE_NAME, path="/")
        return AuthMeResponse(account=None)

    @router.get("/api/auth/me", response_model=AuthMeResponse)
    def me(request: Request) -> AuthMeResponse:
        storage = require_repository(repository)
        account_id = sessions.account_id_for_token(request.cookies.get(SESSION_COOKIE_NAME))
        if account_id is None:
            return AuthMeResponse(account=None)
        try:
            account = storage.get_account(account_id)
        except ValueError:
            return AuthMeResponse(account=None)
        return AuthMeResponse(account=_account_response(account))

    return router


def _account_response(account: AccountEntity) -> AccountResponse:
    return AccountResponse(
        id=account.id,
        email=account.email,
        display_name=account.display_name,
        active=account.active,
    )
