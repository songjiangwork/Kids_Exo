from datetime import datetime

from pydantic import BaseModel

from kids_exo.web.schemas.base import FromDomainModel


class LearnerCreateRequest(BaseModel):
    nickname: str


class LearnerUpdateRequest(BaseModel):
    nickname: str
    active: bool


class LearnerResponse(FromDomainModel):
    id: int
    nickname: str
    active: bool


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
    expected_answer: int
    last_submitted_answer: int
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
