from kids_exo.online.catalog import get_online_catalog
from kids_exo.persistence.repository import PracticeRepository
from kids_exo.web.schemas import (
    IncorrectQuestionResponse,
    LearnerAnalyticsResponse,
    LearnerMistakeEntryResponse,
    LearnerSkillBreakdownResponse,
    PracticeResultsResponse,
    SavedPracticeSessionResponse,
    SessionSummaryResponse,
    StudentQuestionResponse,
    StudentSessionResponse,
    TimerStatusResponse,
)


def student_questions(saved_session) -> tuple[StudentQuestionResponse, ...]:
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
            audio_url=question_audio_url(saved_session, question),
        )
        for question in saved_session.questions
    )


def saved_session_response(saved_session) -> SavedPracticeSessionResponse:
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
        questions=student_questions(saved_session),
    )


def question_audio_url(saved_session, question) -> str | None:
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


def elapsed_seconds(saved_session) -> int | None:
    return PracticeRepository._elapsed_seconds(saved_session)


def session_summary_response(saved_session) -> SessionSummaryResponse:
    attempts = [
        question.attempts[0]
        for question in saved_session.questions
        if question.attempts
    ]
    status = display_status(saved_session, attempts)
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
        elapsed_seconds=elapsed_seconds(saved_session),
        created_at=saved_session.created_at,
        completed_at=saved_session.completed_at,
    )


def practice_results_response(saved_session) -> PracticeResultsResponse:
    attempts = [
        (question, question.attempts[0])
        for question in saved_session.questions
        if question.attempts
    ]
    return PracticeResultsResponse(
        status=display_status(saved_session, [attempt for _, attempt in attempts]),
        total_questions=len(saved_session.questions),
        answered_questions=len(attempts),
        correct_answers=sum(attempt.is_correct for _, attempt in attempts),
        elapsed_seconds=elapsed_seconds(saved_session),
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


def timer_status_response(saved_session) -> TimerStatusResponse:
    return TimerStatusResponse(
        timer_status=PracticeRepository._timer_status(saved_session),
        active_elapsed_seconds=saved_session.active_elapsed_seconds or 0,
    )


def student_session_response(saved_session) -> StudentSessionResponse:
    attempts = [
        question.attempts[0]
        for question in saved_session.questions
        if question.attempts
    ]
    return StudentSessionResponse(
        plugin=saved_session.plugin,
        subject=saved_session.subject,
        category=saved_session.category,
        skill=saved_session.skill,
        status=display_status(saved_session, attempts),
        timer_status=PracticeRepository._timer_status(saved_session),
        requested_locale=saved_session.requested_locale,
        feedback_mode=saved_session.feedback_mode,
        show_timer=saved_session.show_timer,
        answered_questions=len(attempts),
        correct_answers=sum(attempt.is_correct for attempt in attempts),
        active_elapsed_seconds=saved_session.active_elapsed_seconds or 0,
        questions=student_questions(saved_session),
    )


def display_status(saved_session, attempts) -> str:
    if saved_session.questions and len(attempts) == len(saved_session.questions):
        return "completed"
    if attempts:
        return "in_progress"
    return saved_session.status


def plugin_title(plugin_name: str) -> str:
    for plugin in get_online_catalog().plugins:
        if plugin.plugin == plugin_name:
            return plugin.title
    return plugin_name


def learner_analytics_response(analytics) -> LearnerAnalyticsResponse:
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
                title=plugin_title(item.plugin),
                correct_answers=item.correct_answers,
                total_questions=item.total_questions,
                accuracy=item.accuracy,
            )
            for item in analytics.skill_breakdown
        ),
        mistake_notebook=tuple(
            LearnerMistakeEntryResponse(
                plugin=item.plugin,
                title=plugin_title(item.plugin),
                prompt=item.prompt,
                expected_answer=item.expected_answer,
                last_submitted_answer=item.last_submitted_answer,
                times_missed=item.times_missed,
                last_seen_at=item.last_seen_at,
            )
            for item in analytics.mistake_notebook
        ),
    )
