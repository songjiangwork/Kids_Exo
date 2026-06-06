import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import Response

from kids_exo.catalog import list_preset_entries
from kids_exo.online.catalog import get_online_catalog
from kids_exo.online.session import OnlineSessionRequest, create_practice_session
from kids_exo.persistence.database import build_engine, build_session_factory
from kids_exo.persistence.repository import PracticeRepository
from kids_exo.printable import generate_printable_pdf
from kids_exo.web.schemas import (
    AnswerSubmissionRequest,
    AnswerSubmissionResponse,
    LearnerAnalyticsResponse,
    LearnerCreateRequest,
    LearnerMistakeEntryResponse,
    LearnerResponse,
    LearnerSkillBreakdownResponse,
    LearnerUpdateRequest,
    OnlineCatalogResponse,
    IncorrectQuestionResponse,
    PracticeResultsResponse,
    PracticePreviewRequest,
    PracticePreviewResponse,
    PrintablePdfRequest,
    PrintableWorksheetResponse,
    SavedPracticeSessionResponse,
    SessionSummaryResponse,
    StudentQuestionResponse,
    StudentSessionResponse,
    TimerStatusResponse,
)


def create_app(repository: PracticeRepository | None = None) -> FastAPI:
    app = FastAPI(title="Kids Exo API", version="0.1.0")

    @app.get("/api/practice-plugins", response_model=OnlineCatalogResponse)
    def list_practice_plugins() -> OnlineCatalogResponse:
        return OnlineCatalogResponse.model_validate(get_online_catalog())

    @app.get(
        "/api/printable-worksheets",
        response_model=list[PrintableWorksheetResponse],
    )
    def list_printable_worksheets() -> list[PrintableWorksheetResponse]:
        return [
            PrintableWorksheetResponse.model_validate(entry)
            for entry in list_preset_entries()
        ]

    @app.post("/api/printable-worksheets/pdf")
    def download_printable_pdf(request: PrintablePdfRequest) -> Response:
        try:
            pdf = generate_printable_pdf(
                request.preset_id,
                seed=request.seed,
                include_warmup=request.include_warmup,
                page_count=request.page_count,
                question_count=request.question_count,
            )
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return Response(
            content=pdf.content,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="{pdf.filename}"',
            },
        )

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
            subject=session.subject,
            category=session.category,
            skill=session.skill,
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

    @app.get("/api/learners", response_model=list[LearnerResponse])
    def list_learners() -> list[LearnerResponse]:
        storage = _require_repository(repository)
        return [
            LearnerResponse.model_validate(learner)
            for learner in storage.list_learners()
        ]

    @app.get("/api/learners/{learner_id}", response_model=LearnerResponse)
    def get_learner(learner_id: int) -> LearnerResponse:
        storage = _require_repository(repository)
        try:
            return LearnerResponse.model_validate(storage.get_learner(learner_id))
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get("/api/learners/{learner_id}/analytics", response_model=LearnerAnalyticsResponse)
    def get_learner_analytics(learner_id: int) -> LearnerAnalyticsResponse:
        storage = _require_repository(repository)
        try:
            return _learner_analytics_response(storage.get_learner_analytics(learner_id))
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.patch("/api/learners/{learner_id}", response_model=LearnerResponse)
    def update_learner(
        learner_id: int,
        request: LearnerUpdateRequest,
    ) -> LearnerResponse:
        storage = _require_repository(repository)
        try:
            return LearnerResponse.model_validate(
                storage.update_learner(
                    learner_id,
                    nickname=request.nickname,
                    active=request.active,
                )
            )
        except ValueError as exc:
            status_code = 404 if str(exc).startswith("Unknown learner") else 422
            raise HTTPException(status_code=status_code, detail=str(exc)) from exc

    @app.delete("/api/learners/{learner_id}", status_code=204)
    def delete_learner(learner_id: int) -> None:
        storage = _require_repository(repository)
        try:
            storage.delete_learner(learner_id)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

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
            )
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        return _saved_session_response(saved)

    @app.get(
        "/api/learners/{learner_id}/sessions",
        response_model=list[SessionSummaryResponse],
    )
    def list_learner_sessions(learner_id: int) -> list[SessionSummaryResponse]:
        storage = _require_repository(repository)
        try:
            return [
                _session_summary_response(saved)
                for saved in storage.list_sessions_for_learner(learner_id)
            ]
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc

    @app.get(
        "/api/learners/{learner_id}/sessions/{session_id}/results",
        response_model=PracticeResultsResponse,
    )
    def get_parent_session_results(
        learner_id: int,
        session_id: int,
    ) -> PracticeResultsResponse:
        storage = _require_repository(repository)
        try:
            saved = storage.get_results_for_learner(learner_id, session_id)
        except ValueError as exc:
            status_code = 409 if "not completed" in str(exc) else 404
            raise HTTPException(status_code=status_code, detail=str(exc)) from exc
        return _practice_results_response(saved)

    @app.get(
        "/api/student/sessions/{token}",
        response_model=StudentSessionResponse,
    )
    def get_student_session(token: str) -> StudentSessionResponse:
        storage = _require_repository(repository)
        try:
            storage.start_student_session(token)
            saved = storage.get_session_by_student_token(token)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        attempts = [
            question.attempts[0]
            for question in saved.questions
            if question.attempts
        ]
        return StudentSessionResponse(
            plugin=saved.plugin,
            subject=saved.subject,
            category=saved.category,
            skill=saved.skill,
            status=_display_status(saved, attempts),
            timer_status=PracticeRepository._timer_status(saved),
            requested_locale=saved.requested_locale,
            feedback_mode=saved.feedback_mode,
            show_timer=saved.show_timer,
            answered_questions=len(attempts),
            correct_answers=sum(attempt.is_correct for attempt in attempts),
            active_elapsed_seconds=saved.active_elapsed_seconds or 0,
            questions=_student_questions(saved),
        )

    @app.post(
        "/api/student/sessions/{token}/timer/pause",
        response_model=TimerStatusResponse,
    )
    def pause_student_timer(token: str) -> TimerStatusResponse:
        storage = _require_repository(repository)
        try:
            saved = storage.pause_student_timer(token)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return _timer_status_response(saved)

    @app.post(
        "/api/student/sessions/{token}/timer/resume",
        response_model=TimerStatusResponse,
    )
    def resume_student_timer(token: str) -> TimerStatusResponse:
        storage = _require_repository(repository)
        try:
            saved = storage.resume_student_timer(token)
        except ValueError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        return _timer_status_response(saved)

    @app.get(
        "/api/student/sessions/{token}/results",
        response_model=PracticeResultsResponse,
    )
    def get_student_session_results(token: str) -> PracticeResultsResponse:
        storage = _require_repository(repository)
        try:
            saved = storage.get_completed_results_by_student_token(token)
        except ValueError as exc:
            status_code = 409 if "not completed" in str(exc) else 404
            raise HTTPException(status_code=status_code, detail=str(exc)) from exc
        return _practice_results_response(saved)

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
            renderer_type=getattr(question, "renderer_type", "numeric_answer"),
            prompt_payload=dict(getattr(question, "prompt_payload", {}) or {}),
            public_payload=dict(getattr(question, "public_payload", {}) or {}),
            question_type=question.question_type,
            choices=tuple(question.choices or ()),
            speech_text=question.speech_text,
            speech_locale=question.speech_locale,
            audio_url=_question_audio_url(saved_session, question),
        )
        for question in saved_session.questions
    )


def _saved_session_response(saved_session) -> SavedPracticeSessionResponse:
    return SavedPracticeSessionResponse(
        id=saved_session.id,
        student_token=saved_session.student_token,
        plugin=saved_session.plugin,
        subject=saved_session.subject,
        category=saved_session.category,
        skill=saved_session.skill,
        requested_locale=saved_session.requested_locale,
        feedback_mode=saved_session.feedback_mode,
        show_timer=saved_session.show_timer,
        localization_fallback_keys=tuple(saved_session.localization_fallback_keys),
        questions=_student_questions(saved_session),
    )


def _question_audio_url(saved_session, question) -> str | None:
    if question.audio_url:
        return question.audio_url
    if (
        saved_session.plugin == "french_alphabet_sounds"
        and question.strategy == "letter_name_to_letter"
        and question.speech_text
        and len(question.speech_text) == 1
    ):
        return f"/audio/tts/fr/fr-FR-DeniseNeural/alphabet/{question.speech_text.lower()}.mp3"
    return None


def _elapsed_seconds(saved_session) -> int | None:
    return PracticeRepository._elapsed_seconds(saved_session)


def _session_summary_response(saved_session) -> SessionSummaryResponse:
    attempts = [
        question.attempts[0]
        for question in saved_session.questions
        if question.attempts
    ]
    status = _display_status(saved_session, attempts)
    return SessionSummaryResponse(
        id=saved_session.id,
        student_token=saved_session.student_token,
        plugin=saved_session.plugin,
        subject=saved_session.subject,
        category=saved_session.category,
        skill=saved_session.skill,
        status=status,
        total_questions=len(saved_session.questions),
        answered_questions=len(attempts),
        correct_answers=sum(attempt.is_correct for attempt in attempts),
        elapsed_seconds=_elapsed_seconds(saved_session),
        created_at=saved_session.created_at,
        completed_at=saved_session.completed_at,
    )


def _practice_results_response(saved_session) -> PracticeResultsResponse:
    attempts = [
        (question, question.attempts[0])
        for question in saved_session.questions
        if question.attempts
    ]
    return PracticeResultsResponse(
        status=_display_status(saved_session, [attempt for _, attempt in attempts]),
        total_questions=len(saved_session.questions),
        answered_questions=len(attempts),
        correct_answers=sum(attempt.is_correct for _, attempt in attempts),
        elapsed_seconds=_elapsed_seconds(saved_session),
        incorrect_questions=tuple(
            IncorrectQuestionResponse(
                prompt=question.prompt,
                submitted_answer=attempt.normalized_answer,
                expected_answer=question.expected_answer,
            )
            for question, attempt in attempts
            if not attempt.is_correct
        ),
    )


def _timer_status_response(saved_session) -> TimerStatusResponse:
    return TimerStatusResponse(
        timer_status=PracticeRepository._timer_status(saved_session),
        active_elapsed_seconds=saved_session.active_elapsed_seconds or 0,
    )


def _display_status(saved_session, attempts) -> str:
    if saved_session.questions and len(attempts) == len(saved_session.questions):
        return "completed"
    if attempts:
        return "in_progress"
    return saved_session.status


def _plugin_title(plugin_name: str) -> str:
    for plugin in get_online_catalog().plugins:
        if plugin.plugin == plugin_name:
            return plugin.title
    return plugin_name


def _learner_analytics_response(analytics) -> LearnerAnalyticsResponse:
    return LearnerAnalyticsResponse(
        total_sessions=analytics.total_sessions,
        completed_sessions=analytics.completed_sessions,
        total_questions=analytics.total_questions,
        correct_answers=analytics.correct_answers,
        accuracy=analytics.accuracy,
        average_elapsed_seconds=analytics.average_elapsed_seconds,
        last_completed_at=analytics.last_completed_at,
        skill_breakdown=tuple(
            LearnerSkillBreakdownResponse(
                plugin=item.plugin,
                title=_plugin_title(item.plugin),
                correct_answers=item.correct_answers,
                total_questions=item.total_questions,
                accuracy=item.accuracy,
            )
            for item in analytics.skill_breakdown
        ),
        mistake_notebook=tuple(
            LearnerMistakeEntryResponse(
                plugin=item.plugin,
                title=_plugin_title(item.plugin),
                prompt=item.prompt,
                expected_answer=item.expected_answer,
                last_submitted_answer=item.last_submitted_answer,
                times_missed=item.times_missed,
                last_seen_at=item.last_seen_at,
            )
            for item in analytics.mistake_notebook
        ),
    )


def _default_repository() -> PracticeRepository:
    database_url = os.environ.get(
        "KIDS_EXO_DATABASE_URL",
        "sqlite+pysqlite:///kids-exo.db",
    )
    return PracticeRepository(build_session_factory(build_engine(database_url)))


app = create_app(_default_repository())
