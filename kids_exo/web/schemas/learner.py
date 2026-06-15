from datetime import datetime
from typing import Any

from pydantic import BaseModel

from kids_exo.web.schemas.base import FromDomainModel


class LearnerCreateRequest(BaseModel):
    nickname: str


class LearnerUpdateRequest(BaseModel):
    nickname: str
    active: bool


class StudentPinResetRequest(BaseModel):
    pin: str


class LearnerResponse(FromDomainModel):
    id: int
    nickname: str
    active: bool
    student_code: str | None = None


class LearnerSkillBreakdownResponse(FromDomainModel):
    plugin: str
    title: str
    correct_answers: int
    total_questions: int
    accuracy: float


class LearnerMistakeEntryResponse(BaseModel):
    plugin: str
    title: str
    prompt: str
    expected_answer: int | str | dict[str, Any] | None
    last_submitted_answer: int | str | dict[str, Any] | None
    expected_display: str | None = None
    last_submitted_display: str | None = None
    answer_type: str | None = None
    times_missed: int
    last_seen_at: datetime


class LearnerAnalyticsResponse(BaseModel):
    total_sessions: int
    completed_sessions: int
    total_questions: int
    correct_answers: int
    accuracy: float
    average_elapsed_seconds: int | None
    last_completed_at: datetime | None
    skill_breakdown: tuple[LearnerSkillBreakdownResponse, ...]
    mistake_notebook: tuple[LearnerMistakeEntryResponse, ...]
