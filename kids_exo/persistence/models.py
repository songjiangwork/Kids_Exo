from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class AccountEntity(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(160))
    password_hash: Mapped[str] = mapped_column(String(255))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    owned_households: Mapped[list["HouseholdEntity"]] = relationship(
        back_populates="owner_account",
        foreign_keys="HouseholdEntity.owner_account_id",
    )
    household_memberships: Mapped[list["HouseholdMemberEntity"]] = relationship(
        back_populates="account",
        cascade="all, delete-orphan",
    )
    learner_profile: Mapped["LearnerEntity | None"] = relationship(
        back_populates="optional_account",
    )


class HouseholdEntity(Base):
    __tablename__ = "households"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(160))
    owner_account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    owner_account: Mapped[AccountEntity] = relationship(
        back_populates="owned_households",
        foreign_keys=[owner_account_id],
    )
    members: Mapped[list["HouseholdMemberEntity"]] = relationship(
        back_populates="household",
        cascade="all, delete-orphan",
    )
    learners: Mapped[list["LearnerEntity"]] = relationship(back_populates="household")


class HouseholdMemberEntity(Base):
    __tablename__ = "household_members"
    __table_args__ = (
        UniqueConstraint("household_id", "account_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    household_id: Mapped[int] = mapped_column(ForeignKey("households.id"))
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"))
    role: Mapped[str] = mapped_column(String(30))
    parent_unlock_pin_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    parent_unlock_pin_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    household: Mapped[HouseholdEntity] = relationship(back_populates="members")
    account: Mapped[AccountEntity] = relationship(back_populates="household_memberships")


class LearnerEntity(Base):
    __tablename__ = "learners"

    id: Mapped[int] = mapped_column(primary_key=True)
    household_id: Mapped[int] = mapped_column(ForeignKey("households.id"))
    nickname: Mapped[str] = mapped_column(String(100))
    avatar_key: Mapped[str] = mapped_column(String(40), default="fox")
    student_login_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    student_code: Mapped[str | None] = mapped_column(String(80), nullable=True)
    student_pin_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    student_pin_updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    student_login_failed_count: Mapped[int] = mapped_column(Integer, default=0)
    student_login_locked_until: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    optional_account_id: Mapped[int | None] = mapped_column(
        ForeignKey("accounts.id"),
        nullable=True,
    )
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    household: Mapped[HouseholdEntity] = relationship(back_populates="learners")
    optional_account: Mapped[AccountEntity | None] = relationship(back_populates="learner_profile")
    practice_sessions: Mapped[list["PracticeSessionEntity"]] = relationship(
        back_populates="learner",
        cascade="all, delete-orphan",
    )
    assignments: Mapped[list["AssignmentEntity"]] = relationship(
        back_populates="learner",
        cascade="all, delete-orphan",
    )


class PracticeSessionEntity(Base):
    __tablename__ = "practice_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)
    learner_id: Mapped[int] = mapped_column(ForeignKey("learners.id"))
    student_token: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    plugin: Mapped[str] = mapped_column(String(100))
    subject: Mapped[str] = mapped_column(String(80), default="Math")
    category: Mapped[str] = mapped_column(String(120), default="Mental Multiplication")
    skill: Mapped[str] = mapped_column(String(160), default="")
    plugin_settings: Mapped[dict[str, Any]] = mapped_column(JSON)
    requested_locale: Mapped[str] = mapped_column(String(20))
    feedback_mode: Mapped[str] = mapped_column(String(20))
    show_timer: Mapped[bool] = mapped_column(Boolean)
    seed: Mapped[int | None] = mapped_column(Integer, nullable=True)
    localization_fallback_keys: Mapped[list[str]] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(20), default="created")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    active_elapsed_seconds: Mapped[int] = mapped_column(Integer, default=0)
    timer_started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_answered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    learner: Mapped[LearnerEntity] = relationship(back_populates="practice_sessions")
    assignment_items: Mapped[list["AssignmentItemEntity"]] = relationship(
        back_populates="linked_session",
    )
    questions: Mapped[list["QuestionInstanceEntity"]] = relationship(
        back_populates="practice_session",
        cascade="all, delete-orphan",
        order_by="QuestionInstanceEntity.position",
    )


class AssignmentEntity(Base):
    __tablename__ = "assignments"

    id: Mapped[int] = mapped_column(primary_key=True)
    learner_id: Mapped[int] = mapped_column(ForeignKey("learners.id"))
    title: Mapped[str] = mapped_column(String(160))
    description: Mapped[str] = mapped_column(String(1000), default="")
    status: Mapped[str] = mapped_column(String(30), default="assigned")
    source_type: Mapped[str] = mapped_column(String(40), default="parent_assigned")
    due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_by_role: Mapped[str] = mapped_column(String(30), default="parent")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    learner: Mapped[LearnerEntity] = relationship(back_populates="assignments")
    items: Mapped[list["AssignmentItemEntity"]] = relationship(
        back_populates="assignment",
        cascade="all, delete-orphan",
        order_by="AssignmentItemEntity.order_index",
    )


class AssignmentItemEntity(Base):
    __tablename__ = "assignment_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    assignment_id: Mapped[int] = mapped_column(ForeignKey("assignments.id"))
    item_type: Mapped[str] = mapped_column(String(40), default="practice_plugin")
    plugin: Mapped[str] = mapped_column(String(100))
    plugin_settings: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    question_count: Mapped[int] = mapped_column(Integer)
    feedback_mode: Mapped[str] = mapped_column(String(20), default="immediate")
    show_timer: Mapped[bool] = mapped_column(Boolean, default=True)
    order_index: Mapped[int] = mapped_column(Integer, default=1)
    required: Mapped[bool] = mapped_column(Boolean, default=True)
    status: Mapped[str] = mapped_column(String(30), default="assigned")
    linked_session_id: Mapped[int | None] = mapped_column(
        ForeignKey("practice_sessions.id"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    assignment: Mapped[AssignmentEntity] = relationship(back_populates="items")
    linked_session: Mapped[PracticeSessionEntity | None] = relationship(
        back_populates="assignment_items",
    )


class QuestionInstanceEntity(Base):
    __tablename__ = "question_instances"
    __table_args__ = (
        UniqueConstraint("practice_session_id", "public_identifier"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    practice_session_id: Mapped[int] = mapped_column(ForeignKey("practice_sessions.id"))
    public_identifier: Mapped[str] = mapped_column(String(60))
    position: Mapped[int] = mapped_column(Integer)
    prompt: Mapped[str] = mapped_column(String(300))
    strategy: Mapped[str] = mapped_column(String(100))
    expected_answer: Mapped[int | None] = mapped_column(Integer, nullable=True)
    skill_tags: Mapped[list[str]] = mapped_column(JSON)
    renderer_type: Mapped[str] = mapped_column(String(80), default="numeric_answer")
    answer_type: Mapped[str] = mapped_column(String(80), default="integer_exact")
    evaluation_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    prompt_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    public_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    question_type: Mapped[str] = mapped_column(String(30), default="numeric")
    choices: Mapped[list[str]] = mapped_column(JSON, default=list)
    speech_text: Mapped[str | None] = mapped_column(String(300), nullable=True)
    speech_locale: Mapped[str | None] = mapped_column(String(20), nullable=True)
    audio_url: Mapped[str | None] = mapped_column(String(300), nullable=True)
    practice_session: Mapped[PracticeSessionEntity] = relationship(back_populates="questions")
    attempts: Mapped[list["ResponseAttemptEntity"]] = relationship(
        back_populates="question",
        cascade="all, delete-orphan",
        order_by="ResponseAttemptEntity.attempt_number",
    )


class ResponseAttemptEntity(Base):
    __tablename__ = "response_attempts"

    id: Mapped[int] = mapped_column(primary_key=True)
    question_instance_id: Mapped[int] = mapped_column(ForeignKey("question_instances.id"))
    attempt_number: Mapped[int] = mapped_column(Integer)
    submitted_answer: Mapped[str] = mapped_column(String(100))
    normalized_answer: Mapped[int | None] = mapped_column(Integer, nullable=True)
    submitted_payload: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    normalized_payload: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    evaluation_detail: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    is_correct: Mapped[bool] = mapped_column(Boolean)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    question: Mapped[QuestionInstanceEntity] = relationship(back_populates="attempts")
