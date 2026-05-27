from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class FromDomainModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class SettingOptionResponse(FromDomainModel):
    value: int | str
    label: str


class PluginSettingSchemaResponse(FromDomainModel):
    name: str
    label: str
    control: str
    default: tuple[int | str, ...]
    options: tuple[SettingOptionResponse, ...]


class LocaleCoverageResponse(FromDomainModel):
    locale: str
    full_sections: tuple[str, ...]
    partial_sections: tuple[str, ...]


class OnlinePluginResponse(FromDomainModel):
    plugin: str
    subject: str
    category: str
    title: str
    description: str
    default_locale: str
    locale_coverage: tuple[LocaleCoverageResponse, ...]
    settings: tuple[PluginSettingSchemaResponse, ...]


class OnlineCatalogResponse(FromDomainModel):
    default_locale: str
    question_counts: tuple[int, ...]
    feedback_modes: tuple[str, ...]
    show_timer_configurable: bool
    plugins: tuple[OnlinePluginResponse, ...]


class PrintableWorksheetResponse(FromDomainModel):
    identifier: str
    subject: str
    category: str
    title: str


class PrintablePdfRequest(BaseModel):
    preset_id: str
    seed: int | None = None
    include_warmup: bool = True
    page_count: int = Field(default=1, ge=1, le=20)
    question_count: int | None = Field(default=None, ge=1, le=500)


class PracticePreviewRequest(BaseModel):
    plugin: str
    plugin_settings: dict[str, Any] = Field(default_factory=dict)
    question_count: int
    requested_locale: str = "en-CA"
    feedback_mode: str = "immediate"
    show_timer: bool = False
    seed: int | None = None


class StudentQuestionResponse(FromDomainModel):
    identifier: str
    position: int
    total_questions: int
    prompt: str


class PracticePreviewResponse(BaseModel):
    plugin: str
    requested_locale: str
    feedback_mode: str
    show_timer: bool
    localization_fallback_keys: tuple[str, ...]
    questions: tuple[StudentQuestionResponse, ...]


class LearnerCreateRequest(BaseModel):
    nickname: str


class LearnerResponse(FromDomainModel):
    id: int
    nickname: str
    active: bool


class SessionSummaryResponse(BaseModel):
    id: int
    student_token: str
    plugin: str
    status: str
    total_questions: int
    answered_questions: int
    correct_answers: int
    elapsed_seconds: int | None
    created_at: datetime
    completed_at: datetime | None


class IncorrectQuestionResponse(BaseModel):
    prompt: str
    submitted_answer: int
    expected_answer: int


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
    requested_locale: str
    feedback_mode: str
    show_timer: bool
    localization_fallback_keys: tuple[str, ...]
    questions: tuple[StudentQuestionResponse, ...]


class StudentSessionResponse(BaseModel):
    plugin: str
    requested_locale: str
    feedback_mode: str
    show_timer: bool
    questions: tuple[StudentQuestionResponse, ...]


class AnswerSubmissionRequest(BaseModel):
    answer: str


class AnswerSubmissionResponse(FromDomainModel):
    normalized_answer: int
    is_correct: bool | None
