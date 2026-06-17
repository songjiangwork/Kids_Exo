from kids_exo.online.answer_display import (
    AnswerValue,
    answer_display,
    choice_label,
    expected_answer_display_for_question,
    expected_answer_value_for_question,
    submitted_answer_value_for_attempt,
)
from kids_exo.online.catalog import get_online_catalog
from kids_exo.persistence.repository import PracticeRepository
from kids_exo.web.schemas import (
    AssignmentItemResponse,
    AssignmentResponse,
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
                submitted_answer=submitted_answer_value(attempt),
                expected_answer=expected_answer_value(question),
                submitted_display=submitted_answer_display(attempt, question),
                expected_display=expected_answer_display(question),
                submitted_work=submitted_work(attempt),
                feedback_code=feedback_code(attempt),
                answer_type=question.answer_type,
            )
            for question, attempt in attempts
            if not attempt.is_correct
        ),
    )


def submitted_answer_value(attempt) -> AnswerValue:
    return submitted_answer_value_for_attempt(attempt)


def expected_answer_value(question) -> AnswerValue:
    return expected_answer_value_for_question(question)


def submitted_answer_display(attempt, question=None) -> str | None:
    value = submitted_answer_value(attempt)
    if question is not None and getattr(question, "answer_type", None) == "multiple_choice_index":
        choice = _choice_label(question, value)
        if choice is not None:
            return choice
    return _display_answer(value)


def submitted_work(attempt) -> str | None:
    value = submitted_answer_value(attempt)
    if isinstance(value, dict):
        work = value.get("work")
        if isinstance(work, str) and work:
            return work
    payload = getattr(attempt, "submitted_payload", None) or {}
    raw = payload.get("raw")
    if isinstance(raw, dict):
        work = raw.get("work")
        if isinstance(work, str) and work:
            return work
    return None


def feedback_code(attempt) -> str | None:
    detail = getattr(attempt, "evaluation_detail", None) or {}
    code = detail.get("feedback_code")
    return str(code) if code else None


def expected_answer_display(question) -> str | None:
    return expected_answer_display_for_question(question)


def _choice_label(question, value: AnswerValue) -> str | None:
    choices = tuple(getattr(question, "choices", ()) or ())
    return choice_label(value, choices)


def _display_answer(value: AnswerValue) -> str | None:
    return answer_display(value)


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
                expected_display=item.expected_display,
                last_submitted_display=item.last_submitted_display,
                answer_type=item.answer_type,
                times_missed=item.times_missed,
                last_seen_at=item.last_seen_at,
            )
            for item in analytics.mistake_notebook
        ),
    )


def assignment_response(assignment) -> AssignmentResponse:
    return AssignmentResponse(
        id=assignment.id,
        learner_id=assignment.learner_id,
        title=assignment.title,
        description=assignment.description,
        status=assignment.status,
        source_type=assignment.source_type,
        due_at=assignment.due_at,
        created_by_role=assignment.created_by_role,
        created_at=assignment.created_at,
        updated_at=assignment.updated_at,
        completed_at=assignment.completed_at,
        items=tuple(assignment_item_response(item) for item in assignment.items),
    )


def assignment_item_response(item) -> AssignmentItemResponse:
    linked = item.__dict__.get("linked_session")
    return AssignmentItemResponse(
        id=item.id,
        item_type=item.item_type,
        plugin=item.plugin,
        plugin_settings=item.plugin_settings,
        question_count=item.question_count,
        feedback_mode=item.feedback_mode,
        show_timer=item.show_timer,
        order_index=item.order_index,
        required=item.required,
        status=item.status,
        linked_session_id=item.linked_session_id,
        student_token=(linked.student_token if linked is not None else None),
        skill=(linked.skill if linked is not None else None),
        subject=(linked.subject if linked is not None else None),
        category=(linked.category if linked is not None else None),
        created_at=item.created_at,
        completed_at=item.completed_at,
    )
