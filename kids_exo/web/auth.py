import secrets
from dataclasses import dataclass, field
from typing import Callable

from fastapi import HTTPException, Request

from kids_exo.persistence.models import AccountEntity, HouseholdMemberEntity
from kids_exo.persistence.repository import PracticeRepository
from kids_exo.web.dependencies import require_repository


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


def current_account_or_none(
    repository: PracticeRepository | None,
    session_store: LocalSessionStore,
) -> Callable[[Request], AccountEntity | None]:
    def dependency(request: Request) -> AccountEntity | None:
        storage = require_repository(repository)
        account_id = session_store.account_id_for_token(request.cookies.get(SESSION_COOKIE_NAME))
        if account_id is None:
            return None
        try:
            return storage.get_account(account_id)
        except ValueError:
            return None

    return dependency


def require_current_account(
    repository: PracticeRepository | None,
    session_store: LocalSessionStore,
) -> Callable[[Request], AccountEntity]:
    def dependency(request: Request) -> AccountEntity:
        account = current_account_or_none(repository, session_store)(request)
        if account is None:
            raise HTTPException(status_code=401, detail="Authentication required")
        if not account.active:
            raise HTTPException(status_code=403, detail="Account is inactive")
        return account

    return dependency


def require_parent_account(
    repository: PracticeRepository | None,
    session_store: LocalSessionStore,
) -> Callable[[Request], AccountEntity]:
    def dependency(request: Request) -> AccountEntity:
        account = require_current_account(repository, session_store)(request)
        storage = require_repository(repository)
        memberships = storage.list_household_memberships_for_account(account.id)
        if not _has_parent_membership(memberships):
            raise HTTPException(status_code=403, detail="Parent account required")
        return account

    return dependency


def _has_parent_membership(memberships: list[HouseholdMemberEntity]) -> bool:
    return any(membership.role in {"parent", "admin"} for membership in memberships)
