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
