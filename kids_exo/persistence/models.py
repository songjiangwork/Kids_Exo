from datetime import datetime, timezone
from typing import Any

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, String, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class LearnerEntity(Base):
    __tablename__ = "learners"

    id: Mapped[int] = mapped_column(primary_key=True)
    nickname: Mapped[str] = mapped_column(String(100))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    practice_sessions: Mapped[list["PracticeSessionEntity"]] = relationship(
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
    questions: Mapped[list["QuestionInstanceEntity"]] = relationship(
        back_populates="practice_session",
        cascade="all, delete-orphan",
        order_by="QuestionInstanceEntity.position",
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
    expected_answer: Mapped[int] = mapped_column(Integer)
    skill_tags: Mapped[list[str]] = mapped_column(JSON)
    question_type: Mapped[str] = mapped_column(String(30), default="numeric")
    choices: Mapped[list[str]] = mapped_column(JSON, default=list)
    speech_text: Mapped[str | None] = mapped_column(String(300), nullable=True)
    speech_locale: Mapped[str | None] = mapped_column(String(20), nullable=True)
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
    normalized_answer: Mapped[int] = mapped_column(Integer)
    is_correct: Mapped[bool] = mapped_column(Boolean)
    submitted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    question: Mapped[QuestionInstanceEntity] = relationship(back_populates="attempts")
