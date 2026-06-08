from fastapi import APIRouter, HTTPException

from kids_exo.persistence.repository import PracticeRepository
from kids_exo.web.dependencies import create_snapshot, require_repository
from kids_exo.web.mappers import (
    practice_results_response,
    saved_session_response,
    session_summary_response,
)
from kids_exo.web.schemas import (
    PracticePreviewRequest,
    PracticePreviewResponse,
    PracticeResultsResponse,
    SavedPracticeSessionResponse,
    SessionSummaryResponse,
)


def create_router(repository: PracticeRepository | None) -> APIRouter:
    router = APIRouter()

    @router.post("/api/practice-sessions/preview", response_model=PracticePreviewResponse)
    def create_practice_preview(
        request: PracticePreviewRequest,
    ) -> PracticePreviewResponse:
        try:
            session = create_snapshot(request)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return PracticePreviewResponse(
            plugin=session.plugin,
            subject=session.subject,
            category=session.category,
            skill=session.skill,
            requested_locale=session.requested_locale,
            feedback_mode=session.feedback_mode,
            show_timer=session.show_timer,
            localization_fallback_keys=session.localization_fallback_keys,
            questions=session.student_questions(),
        )

    @router.post(
        "/api/learners/{learner_id}/sessions",
        response_model=SavedPracticeSessionResponse,
        status_code=201,
    )
    def save_practice_session(
        learner_id: int,
        request: PracticePreviewRequest,
    ) -> SavedPracticeSessionResponse:
        storage = require_repository(repository)
        try:
            snapshot = create_snapshot(request)
            saved = storage.create_practice_session(
                learner_id,
                snapshot,
            )
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return saved_session_response(saved)

    @router.get(
        "/api/learners/{learner_id}/sessions",
        response_model=list[SessionSummaryResponse],
    )
    def list_learner_sessions(learner_id: int) -> list[SessionSummaryResponse]:
        storage = require_repository(repository)
        try:
            return [
                session_summary_response(saved)
                for saved in storage.list_sessions_for_learner(learner_id)
            ]
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @router.get(
        "/api/learners/{learner_id}/sessions/{session_id}/results",
        response_model=PracticeResultsResponse,
    )
    def get_parent_session_results(
        learner_id: int,
        session_id: int,
    ) -> PracticeResultsResponse:
        storage = require_repository(repository)
        try:
            saved = storage.get_results_for_learner(learner_id, session_id)
        except ValueError as exc:
            status_code = 409 if "not completed" in str(exc) else 404
            raise HTTPException(status_code=status_code, detail=str(exc)) from exc
        return practice_results_response(saved)

    return router
