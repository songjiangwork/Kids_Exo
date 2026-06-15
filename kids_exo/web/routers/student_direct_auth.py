from fastapi import APIRouter, HTTPException, Request, Response

from kids_exo.persistence.models import LearnerEntity
from kids_exo.persistence.repository import PracticeRepository
from kids_exo.web.auth import LocalSessionStore, SESSION_COOKIE_NAME
from kids_exo.web.dependencies import require_repository
from kids_exo.web.schemas import (
    HouseholdStudentSummaryResponse,
    StudentDirectAuthMeResponse,
    StudentDirectLoginRequest,
    StudentDirectLoginResponse,
)


def create_router(
    repository: PracticeRepository | None,
    session_store: LocalSessionStore,
) -> APIRouter:
    router = APIRouter()

    @router.post("/api/student-direct-auth/login", response_model=StudentDirectLoginResponse)
    def login(request: StudentDirectLoginRequest, response: Response) -> StudentDirectLoginResponse:
        storage = require_repository(repository)
        try:
            student = storage.verify_direct_student_login(
                household_code=request.household_code,
                student_code=request.student_code,
                pin=request.pin,
            )
        except ValueError as exc:
            detail = str(exc)
            raise HTTPException(status_code=403, detail=detail) from exc
        token = session_store.create_student_session(
            household_id=student.household_id,
            student_id=student.id,
        )
        response.set_cookie(
            SESSION_COOKIE_NAME,
            token,
            httponly=True,
            samesite="lax",
            path="/",
        )
        return StudentDirectLoginResponse(
            student=_student_summary(student),
            redirect_to=f"/manage/students/{student.id}",
        )

    @router.post("/api/student-direct-auth/logout", status_code=204)
    def logout(request: Request, response: Response) -> None:
        session_store.delete_session(request.cookies.get(SESSION_COOKIE_NAME))
        response.delete_cookie(SESSION_COOKIE_NAME, path="/")

    @router.get("/api/student-direct-auth/me", response_model=StudentDirectAuthMeResponse)
    def me(request: Request) -> StudentDirectAuthMeResponse:
        storage = require_repository(repository)
        state = session_store.get_state(request.cookies.get(SESSION_COOKIE_NAME))
        if (
            state is None
            or state.session_type != "student"
            or state.household_id is None
            or state.active_student_id is None
        ):
            raise HTTPException(status_code=401, detail="Student authentication required")
        try:
            student = storage.get_learner(state.active_student_id, household_id=state.household_id)
            household = storage.get_household(state.household_id)
        except ValueError as exc:
            raise HTTPException(status_code=401, detail="Student authentication required") from exc
        return StudentDirectAuthMeResponse(
            student=_student_summary(student),
            household={"id": household.id, "name": household.name},
        )

    return router


def _student_summary(student: LearnerEntity) -> HouseholdStudentSummaryResponse:
    return HouseholdStudentSummaryResponse(
        id=student.id,
        nickname=student.nickname,
        avatar_key=student.avatar_key,
        student_login_enabled=student.student_login_enabled,
        student_code=student.student_code,
    )
