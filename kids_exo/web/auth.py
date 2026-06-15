import secrets
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Callable

from fastapi import HTTPException, Request

from kids_exo.persistence.models import AccountEntity, HouseholdMemberEntity
from kids_exo.persistence.repository import PracticeRepository
from kids_exo.web.dependencies import require_repository


SESSION_COOKIE_NAME = "kids_exo_session"


@dataclass
class SessionState:
    session_type: str
    account_id: int | None = None
    household_id: int | None = None
    parent_unlocked_until: datetime | None = None
    active_student_id: int | None = None


@dataclass
class LocalSessionStore:
    _sessions: dict[str, SessionState] = field(default_factory=dict)

    def create_session(self, account_id: int) -> str:
        token = secrets.token_urlsafe(32)
        self._sessions[token] = SessionState(session_type="parent", account_id=account_id)
        return token

    def create_student_session(self, *, household_id: int, student_id: int) -> str:
        token = secrets.token_urlsafe(32)
        self._sessions[token] = SessionState(
            session_type="student",
            household_id=household_id,
            active_student_id=student_id,
        )
        return token

    def get_state(self, token: str | None) -> SessionState | None:
        if token is None:
            return None
        return self._sessions.get(token)

    def account_id_for_token(self, token: str | None) -> int | None:
        state = self.get_state(token)
        if state is None:
            return None
        return state.account_id

    def set_parent_unlocked(self, token: str | None, until: datetime) -> None:
        state = self.get_state(token)
        if state is not None:
            state.parent_unlocked_until = until

    def clear_parent_unlocked(self, token: str | None) -> None:
        state = self.get_state(token)
        if state is not None:
            state.parent_unlocked_until = None

    def is_parent_unlocked(self, token: str | None) -> bool:
        state = self.get_state(token)
        return bool(
            state is not None
            and state.parent_unlocked_until is not None
            and state.parent_unlocked_until > datetime.now(timezone.utc)
        )

    def parent_unlock_expires_at(self, token: str | None) -> datetime | None:
        state = self.get_state(token)
        if state is None or not self.is_parent_unlocked(token):
            return None
        return state.parent_unlocked_until

    def set_active_student(self, token: str | None, student_id: int) -> None:
        state = self.get_state(token)
        if state is not None:
            state.active_student_id = student_id

    def clear_active_student(self, token: str | None) -> None:
        state = self.get_state(token)
        if state is not None:
            state.active_student_id = None

    def active_student_id(self, token: str | None) -> int | None:
        state = self.get_state(token)
        if state is None:
            return None
        return state.active_student_id

    def delete_session(self, token: str | None) -> None:
        if token is not None:
            self._sessions.pop(token, None)


@dataclass(frozen=True)
class ParentContext:
    account: AccountEntity
    household_id: int


@dataclass(frozen=True)
class StudentAccessContext:
    account: AccountEntity | None
    household_id: int
    student_id: int
    parent_unlocked: bool


PARENT_UNLOCK_DURATION = timedelta(minutes=15)


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


def require_parent_context(
    repository: PracticeRepository | None,
    session_store: LocalSessionStore,
) -> Callable[[Request], ParentContext]:
    def dependency(request: Request) -> ParentContext:
        account = require_parent_account(repository, session_store)(request)
        storage = require_repository(repository)
        household_id = storage.get_primary_parent_household_id(account.id)
        return ParentContext(account=account, household_id=household_id)

    return dependency


def require_parent_unlock(
    repository: PracticeRepository | None,
    session_store: LocalSessionStore,
) -> Callable[[Request], ParentContext]:
    parent_context = require_parent_context(repository, session_store)

    def dependency(request: Request) -> ParentContext:
        parent = parent_context(request)
        if not session_store.is_parent_unlocked(request.cookies.get(SESSION_COOKIE_NAME)):
            raise HTTPException(status_code=403, detail="Parent management is locked")
        return parent

    return dependency


def require_student_access(
    repository: PracticeRepository | None,
    session_store: LocalSessionStore,
) -> Callable[[int, Request], StudentAccessContext]:
    parent_context = require_parent_context(repository, session_store)

    def dependency(learner_id: int, request: Request) -> StudentAccessContext:
        token = request.cookies.get(SESSION_COOKIE_NAME)
        storage = require_repository(repository)
        state = session_store.get_state(token)
        if state is not None and state.session_type == "student":
            if state.household_id is None or state.active_student_id != learner_id:
                raise HTTPException(status_code=403, detail="Student access required")
            try:
                storage.get_learner(learner_id, household_id=state.household_id)
            except ValueError as exc:
                raise HTTPException(status_code=404, detail=str(exc)) from exc
            return StudentAccessContext(
                account=None,
                household_id=state.household_id,
                student_id=learner_id,
                parent_unlocked=False,
            )

        parent = parent_context(request)
        try:
            storage.get_learner(learner_id, household_id=parent.household_id)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        if session_store.is_parent_unlocked(token):
            return StudentAccessContext(
                account=parent.account,
                household_id=parent.household_id,
                student_id=learner_id,
                parent_unlocked=True,
            )
        if session_store.active_student_id(token) == learner_id:
            return StudentAccessContext(
                account=parent.account,
                household_id=parent.household_id,
                student_id=learner_id,
                parent_unlocked=False,
            )
        raise HTTPException(status_code=403, detail="Student access required")

    return dependency


def _has_parent_membership(memberships: list[HouseholdMemberEntity]) -> bool:
    return any(membership.role in {"parent", "admin"} for membership in memberships)
