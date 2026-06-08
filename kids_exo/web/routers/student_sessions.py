from fastapi import APIRouter, HTTPException

from kids_exo.persistence.repository import PracticeRepository
from kids_exo.web.dependencies import require_repository
from kids_exo.web.mappers import (
    practice_results_response,
    student_session_response,
    timer_status_response,
)
from kids_exo.web.schemas import (
    AnswerSubmissionRequest,
    AnswerSubmissionResponse,
    PracticeResultsResponse,
    StudentSessionResponse,
    TimerStatusResponse,
)


def create_router(repository: PracticeRepository | None) -> APIRouter:
    router = APIRouter()

    @router.get(
        "/api/student/sessions/{token}",
        response_model=StudentSessionResponse,
    )
    def get_student_session(token: str) -> StudentSessionResponse:
        storage = require_repository(repository)
        try:
            storage.start_student_session(token)
            saved = storage.get_session_by_student_token(token)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return student_session_response(saved)

    @router.post(
        "/api/student/sessions/{token}/timer/pause",
        response_model=TimerStatusResponse,
    )
    def pause_student_timer(token: str) -> TimerStatusResponse:
        storage = require_repository(repository)
        try:
            saved = storage.pause_student_timer(token)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return timer_status_response(saved)

    @router.post(
        "/api/student/sessions/{token}/timer/resume",
        response_model=TimerStatusResponse,
    )
    def resume_student_timer(token: str) -> TimerStatusResponse:
        storage = require_repository(repository)
        try:
            saved = storage.resume_student_timer(token)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return timer_status_response(saved)

    @router.get(
        "/api/student/sessions/{token}/results",
        response_model=PracticeResultsResponse,
    )
    def get_student_session_results(token: str) -> PracticeResultsResponse:
        storage = require_repository(repository)
        try:
            saved = storage.get_completed_results_by_student_token(token)
        except ValueError as exc:
            status_code = 409 if "not completed" in str(exc) else 404
            raise HTTPException(status_code=status_code, detail=str(exc)) from exc
        return practice_results_response(saved)

    @router.post(
        "/api/student/sessions/{token}/questions/{question_identifier}/attempts",
        response_model=AnswerSubmissionResponse,
    )
    def submit_student_answer(
        token: str,
        question_identifier: str,
        request: AnswerSubmissionRequest,
    ) -> AnswerSubmissionResponse:
        storage = require_repository(repository)
        try:
            saved_session = storage.get_session_by_student_token(token)
            attempt = storage.submit_answer(token, question_identifier, request.answer)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return AnswerSubmissionResponse(
            normalized_answer=attempt.normalized_answer,
            is_correct=(
                attempt.is_correct
                if saved_session.feedback_mode == "immediate"
                else None
            ),
        )

    return router
