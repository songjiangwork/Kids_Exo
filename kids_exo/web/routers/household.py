from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Request

from kids_exo.persistence.models import LearnerEntity
from kids_exo.persistence.repository import PracticeRepository
from kids_exo.web.auth import (
    LocalSessionStore,
    PARENT_UNLOCK_DURATION,
    ParentContext,
    SESSION_COOKIE_NAME,
    require_parent_context,
)
from kids_exo.web.dependencies import require_repository
from kids_exo.web.schemas import (
    HouseholdStudentsResponse,
    HouseholdStudentSummaryResponse,
    ParentPinChangeRequest,
    ParentUnlockStatusResponse,
    PinRequest,
    StudentAuthMeResponse,
    StudentLoginResponse,
)


def create_router(
    repository: PracticeRepository | None,
    session_store: LocalSessionStore,
) -> APIRouter:
    router = APIRouter()
    parent_context = require_parent_context(repository, session_store)

    @router.get("/api/household/students", response_model=HouseholdStudentsResponse)
    def list_household_students(
        parent: ParentContext = Depends(parent_context),
    ) -> HouseholdStudentsResponse:
        storage = require_repository(repository)
        students = storage.list_student_switcher_entries(parent.household_id)
        return HouseholdStudentsResponse(
            students=tuple(_student_summary(student) for student in students)
        )

    @router.get("/api/household/entry", response_model=HouseholdStudentsResponse)
    def household_entry(
        parent: ParentContext = Depends(parent_context),
    ) -> HouseholdStudentsResponse:
        return list_household_students(parent)

    @router.post(
        "/api/household/students/{student_id}/login",
        response_model=StudentLoginResponse,
    )
    def login_student(
        student_id: int,
        request: PinRequest,
        fastapi_request: Request,
        parent: ParentContext = Depends(parent_context),
    ) -> StudentLoginResponse:
        storage = require_repository(repository)
        try:
            student = storage.verify_student_pin(
                student_id=student_id,
                household_id=parent.household_id,
                pin=request.pin,
            )
        except ValueError as exc:
            status_code = 404 if str(exc).startswith("Unknown learner") else 403
            raise HTTPException(status_code=status_code, detail=str(exc)) from exc
        session_store.clear_parent_unlocked(fastapi_request.cookies.get(SESSION_COOKIE_NAME))
        session_store.set_active_student(fastapi_request.cookies.get(SESSION_COOKIE_NAME), student.id)
        return StudentLoginResponse(student=_student_summary(student))

    @router.post("/api/household/parent-unlock", response_model=ParentUnlockStatusResponse)
    def unlock_parent(
        request: PinRequest,
        fastapi_request: Request,
        parent: ParentContext = Depends(parent_context),
    ) -> ParentUnlockStatusResponse:
        storage = require_repository(repository)
        try:
            storage.verify_parent_unlock_pin(parent.account.id, parent.household_id, request.pin)
        except ValueError as exc:
            raise HTTPException(status_code=403, detail=str(exc)) from exc
        expires_at = datetime.now(timezone.utc) + PARENT_UNLOCK_DURATION
        token = fastapi_request.cookies.get(SESSION_COOKIE_NAME)
        session_store.set_parent_unlocked(token, expires_at)
        session_store.clear_active_student(token)
        return ParentUnlockStatusResponse(unlocked=True, expires_at=expires_at)

    @router.post("/api/household/parent-lock", response_model=ParentUnlockStatusResponse)
    def lock_parent(fastapi_request: Request) -> ParentUnlockStatusResponse:
        session_store.clear_parent_unlocked(fastapi_request.cookies.get(SESSION_COOKIE_NAME))
        return ParentUnlockStatusResponse(unlocked=False)

    @router.post("/api/household/parent-pin", response_model=ParentUnlockStatusResponse)
    def change_parent_pin(
        request: ParentPinChangeRequest,
        fastapi_request: Request,
        parent: ParentContext = Depends(parent_context),
    ) -> ParentUnlockStatusResponse:
        storage = require_repository(repository)
        try:
            storage.change_parent_unlock_pin(
                parent.account.id,
                parent.household_id,
                current_pin=request.current_pin,
                new_pin=request.new_pin,
            )
        except ValueError as exc:
            status_code = 403 if str(exc) == "Invalid parent PIN" else 422
            raise HTTPException(status_code=status_code, detail=str(exc)) from exc
        expires_at = datetime.now(timezone.utc) + PARENT_UNLOCK_DURATION
        token = fastapi_request.cookies.get(SESSION_COOKIE_NAME)
        session_store.set_parent_unlocked(token, expires_at)
        session_store.clear_active_student(token)
        return ParentUnlockStatusResponse(unlocked=True, expires_at=expires_at)

    @router.get("/api/household/parent-unlock/status", response_model=ParentUnlockStatusResponse)
    def parent_unlock_status(fastapi_request: Request) -> ParentUnlockStatusResponse:
        token = fastapi_request.cookies.get(SESSION_COOKIE_NAME)
        expires_at = session_store.parent_unlock_expires_at(token)
        return ParentUnlockStatusResponse(unlocked=expires_at is not None, expires_at=expires_at)

    @router.get("/api/student-auth/me", response_model=StudentAuthMeResponse)
    def student_me(
        fastapi_request: Request,
        parent: ParentContext = Depends(parent_context),
    ) -> StudentAuthMeResponse:
        student_id = session_store.active_student_id(fastapi_request.cookies.get(SESSION_COOKIE_NAME))
        if student_id is None:
            return StudentAuthMeResponse(student=None)
        storage = require_repository(repository)
        try:
            student = storage.get_learner(student_id, household_id=parent.household_id)
        except ValueError:
            return StudentAuthMeResponse(student=None)
        return StudentAuthMeResponse(student=_student_summary(student))

    @router.post("/api/student-auth/logout", response_model=StudentAuthMeResponse)
    def student_logout(fastapi_request: Request) -> StudentAuthMeResponse:
        session_store.clear_active_student(fastapi_request.cookies.get(SESSION_COOKIE_NAME))
        return StudentAuthMeResponse(student=None)

    return router


def _student_summary(student: LearnerEntity) -> HouseholdStudentSummaryResponse:
    return HouseholdStudentSummaryResponse(
        id=student.id,
        nickname=student.nickname,
        avatar_key=student.avatar_key,
        student_login_enabled=student.student_login_enabled,
    )
