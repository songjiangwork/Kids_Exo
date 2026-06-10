from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class AssignmentItemCreateRequest(BaseModel):
    item_type: str = "practice_plugin"
    plugin: str
    plugin_settings: dict[str, Any] = Field(default_factory=dict)
    question_count: int
    feedback_mode: str = "immediate"
    show_timer: bool = True
    required: bool = True


class AssignmentCreateRequest(BaseModel):
    title: str
    description: str = ""
    source_type: str = "parent_assigned"
    due_at: datetime | None = None
    created_by_role: str = "parent"
    items: tuple[AssignmentItemCreateRequest, ...]


class AssignmentItemResponse(BaseModel):
    id: int
    item_type: str
    plugin: str
    plugin_settings: dict[str, Any]
    question_count: int
    feedback_mode: str
    show_timer: bool
    order_index: int
    required: bool
    status: str
    linked_session_id: int | None
    student_token: str | None = None
    skill: str | None = None
    subject: str | None = None
    category: str | None = None
    created_at: datetime
    completed_at: datetime | None


class AssignmentResponse(BaseModel):
    id: int
    learner_id: int
    title: str
    description: str
    status: str
    source_type: str
    due_at: datetime | None
    created_by_role: str
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None
    items: tuple[AssignmentItemResponse, ...]


class AssignmentItemStartResponse(BaseModel):
    assignment: AssignmentResponse
    item: AssignmentItemResponse
    student_token: str
    student_url: str
