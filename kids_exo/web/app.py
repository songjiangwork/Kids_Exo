import secrets
import os

from fastapi import FastAPI, HTTPException

from kids_exo.online.catalog import get_online_catalog
from kids_exo.online.session import OnlineSessionRequest, create_practice_session
from kids_exo.persistence.database import build_engine, build_session_factory
from kids_exo.persistence.repository import PracticeRepository
from kids_exo.web.schemas import (
    AnswerSubmissionRequest,
    AnswerSubmissionResponse,
    LearnerCreateRequest,
    LearnerResponse,
    OnlineCatalogResponse,
    PracticePreviewRequest,
    PracticePreviewResponse,
    SavedPracticeSessionResponse,
    StudentQuestionResponse,
    StudentSessionResponse,
)


def create_app(repository: PracticeRepository | None = None) -> FastAPI:
    app = FastAPI(title="Kids Exo API", version="0.1.0")

    @app.get("/api/practice-plugins", response_model=OnlineCatalogResponse)
    def list_practice_plugins() -> OnlineCatalogResponse:
        return OnlineCatalogResponse.model_validate(get_online_catalog())

    @app.post("/api/practice-sessions/preview", response_model=PracticePreviewResponse)
    def create_practice_preview(
        request: PracticePreviewRequest,
    ) -> PracticePreviewResponse:
        try:
            session = create_practice_session(
                OnlineSessionRequest(
                    plugin=request.plugin,
                    plugin_settings=request.plugin_settings,
                    question_count=request.question_count,
                    requested_locale=request.requested_locale,
                    feedback_mode=request.feedback_mode,
                    show_timer=request.show_timer,
                    seed=request.seed,
                )
            )
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return PracticePreviewResponse(
            plugin=session.plugin,
            requested_locale=session.requested_locale,
            feedback_mode=session.feedback_mode,
            show_timer=session.show_timer,
            localization_fallback_keys=session.localization_fallback_keys,
            questions=session.student_questions(),
        )

    @app.post("/api/learners", response_model=LearnerResponse, status_code=201)
    def create_learner(request: LearnerCreateRequest) -> LearnerResponse:
        storage = _require_repository(repository)
        try:
            return LearnerResponse.model_validate(storage.create_learner(request.nickname))
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc

    @app.post(
        "/api/learners/{learner_id}/sessions",
        response_model=SavedPracticeSessionResponse,
        status_code=201,
    )
    def save_practice_session(
        learner_id: int,
        request: PracticePreviewRequest,
    ) -> SavedPracticeSessionResponse:
        storage = _require_repository(repository)
        try:
            snapshot = _create_snapshot(request)
            saved = storage.create_practice_session(
                learner_id,
                snapshot,
                student_token=secrets.token_urlsafe(24),
            )
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return _saved_session_response(saved)

    @app.get(
        "/api/student/sessions/{token}",
        response_model=StudentSessionResponse,
    )
    def get_student_session(token: str) -> StudentSessionResponse:
        storage = _require_repository(repository)
        try:
            saved = storage.get_session_by_student_token(token)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return StudentSessionResponse(
            plugin=saved.plugin,
            requested_locale=saved.requested_locale,
            feedback_mode=saved.feedback_mode,
            show_timer=saved.show_timer,
            questions=_student_questions(saved),
        )

    @app.post(
        "/api/student/sessions/{token}/questions/{question_identifier}/attempts",
        response_model=AnswerSubmissionResponse,
    )
    def submit_student_answer(
        token: str,
        question_identifier: str,
        request: AnswerSubmissionRequest,
    ) -> AnswerSubmissionResponse:
        storage = _require_repository(repository)
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

    return app


def _create_snapshot(request: PracticePreviewRequest):
    return create_practice_session(
        OnlineSessionRequest(
            plugin=request.plugin,
            plugin_settings=request.plugin_settings,
            question_count=request.question_count,
            requested_locale=request.requested_locale,
            feedback_mode=request.feedback_mode,
            show_timer=request.show_timer,
            seed=request.seed,
        )
    )


def _require_repository(repository: PracticeRepository | None) -> PracticeRepository:
    if repository is None:
        raise HTTPException(status_code=503, detail="Persistence is not configured")
    return repository


def _student_questions(saved_session) -> tuple[StudentQuestionResponse, ...]:
    total = len(saved_session.questions)
    return tuple(
        StudentQuestionResponse(
            identifier=question.public_identifier,
            position=question.position,
            total_questions=total,
            prompt=question.prompt,
        )
        for question in saved_session.questions
    )


def _saved_session_response(saved_session) -> SavedPracticeSessionResponse:
    return SavedPracticeSessionResponse(
        id=saved_session.id,
        student_token=saved_session.student_token,
        plugin=saved_session.plugin,
        requested_locale=saved_session.requested_locale,
        feedback_mode=saved_session.feedback_mode,
        show_timer=saved_session.show_timer,
        localization_fallback_keys=tuple(saved_session.localization_fallback_keys),
        questions=_student_questions(saved_session),
    )


def _default_repository() -> PracticeRepository:
    database_url = os.environ.get(
        "KIDS_EXO_DATABASE_URL",
        "sqlite+pysqlite:///kids-exo.db",
    )
    return PracticeRepository(build_session_factory(build_engine(database_url)))


app = create_app(_default_repository())
