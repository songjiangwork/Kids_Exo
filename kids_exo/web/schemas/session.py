from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from kids_exo.web.schemas.base import FromDomainModel


class PracticePreviewRequest(BaseModel):
    plugin: str
    plugin_settings: dict[str, Any] = Field(default_factory=dict)
    question_count: int
    requested_locale: str = "en-CA"
    feedback_mode: str = "immediate"
    show_timer: bool = True
    seed: int | None = None


class StudentQuestionResponse(FromDomainModel):
    identifier: str
    position: int
    total_questions: int
    prompt: str
    renderer_type: str = "numeric_answer"
    prompt_payload: dict[str, Any] = Field(default_factory=dict)
    public_payload: dict[str, Any] = Field(default_factory=dict)
    question_type: str = "numeric"
    choices: tuple[str, ...] = ()
    speech_text: str | None = None
    speech_locale: str | None = None
    audio_url: str | None = None


class PracticePreviewResponse(BaseModel):
    plugin: str
    subject: str
    category: str
    skill: str
    requested_locale: str
    feedback_mode: str
    show_timer: bool
    localization_fallback_keys: tuple[str, ...]
    questions: tuple[StudentQuestionResponse, ...]


class SessionSummaryResponse(BaseModel):
    id: int
    student_token: str
    plugin: str
    subject: str
    category: str
    skill: str
    status: str
    total_questions: int
    answered_questions: int
    correct_answers: int
    elapsed_seconds: int | None
    created_at: datetime
    completed_at: datetime | None


class IncorrectQuestionResponse(BaseModel):
    prompt: str
    submitted_answer: int | str | dict[str, Any] | None
    expected_answer: int | str | dict[str, Any] | None
    submitted_display: str | None = None
    expected_display: str | None = None
    submitted_work: str | None = None
    answer_type: str | None = None


class PracticeResultsResponse(BaseModel):
    status: str
    total_questions: int
    answered_questions: int
    correct_answers: int
    elapsed_seconds: int | None
    incorrect_questions: tuple[IncorrectQuestionResponse, ...]


class SavedPracticeSessionResponse(BaseModel):
    id: int
    student_token: str
    plugin: str
    subject: str
    category: str
    skill: str
    requested_locale: str
    feedback_mode: str
    show_timer: bool
    localization_fallback_keys: tuple[str, ...]
    questions: tuple[StudentQuestionResponse, ...]
