from typing import Any

from pydantic import BaseModel

from kids_exo.web.schemas.base import FromDomainModel
from kids_exo.web.schemas.session import StudentQuestionResponse


class StudentSessionResponse(BaseModel):
    plugin: str
    subject: str
    category: str
    skill: str
    status: str
    timer_status: str
    requested_locale: str
    feedback_mode: str
    show_timer: bool
    answered_questions: int
    correct_answers: int
    active_elapsed_seconds: int
    questions: tuple[StudentQuestionResponse, ...]


class TimerStatusResponse(BaseModel):
    timer_status: str
    active_elapsed_seconds: int


class AnswerSubmissionRequest(BaseModel):
    answer: str | int | dict[str, Any]


class AnswerSubmissionResponse(FromDomainModel):
    normalized_answer: int | str | dict[str, Any] | None
    is_correct: bool | None
