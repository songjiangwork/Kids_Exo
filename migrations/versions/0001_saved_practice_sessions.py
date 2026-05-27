"""Create learner and saved practice session tables."""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0001_saved_practice_sessions"
down_revision: str | None = None
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "learners",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nickname", sa.String(length=100), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "practice_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("learner_id", sa.Integer(), nullable=False),
        sa.Column("student_token", sa.String(length=100), nullable=False),
        sa.Column("plugin", sa.String(length=100), nullable=False),
        sa.Column("plugin_settings", sa.JSON(), nullable=False),
        sa.Column("requested_locale", sa.String(length=20), nullable=False),
        sa.Column("feedback_mode", sa.String(length=20), nullable=False),
        sa.Column("show_timer", sa.Boolean(), nullable=False),
        sa.Column("seed", sa.Integer(), nullable=True),
        sa.Column("localization_fallback_keys", sa.JSON(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.ForeignKeyConstraint(["learner_id"], ["learners.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("student_token"),
    )
    op.create_index(
        op.f("ix_practice_sessions_student_token"),
        "practice_sessions",
        ["student_token"],
        unique=True,
    )
    op.create_table(
        "question_instances",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("practice_session_id", sa.Integer(), nullable=False),
        sa.Column("public_identifier", sa.String(length=60), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column("prompt", sa.String(length=300), nullable=False),
        sa.Column("strategy", sa.String(length=100), nullable=False),
        sa.Column("expected_answer", sa.Integer(), nullable=False),
        sa.Column("skill_tags", sa.JSON(), nullable=False),
        sa.ForeignKeyConstraint(["practice_session_id"], ["practice_sessions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("practice_session_id", "public_identifier"),
    )
    op.create_table(
        "response_attempts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("question_instance_id", sa.Integer(), nullable=False),
        sa.Column("attempt_number", sa.Integer(), nullable=False),
        sa.Column("submitted_answer", sa.String(length=100), nullable=False),
        sa.Column("normalized_answer", sa.Integer(), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["question_instance_id"], ["question_instances.id"]),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("response_attempts")
    op.drop_table("question_instances")
    op.drop_index(op.f("ix_practice_sessions_student_token"), table_name="practice_sessions")
    op.drop_table("practice_sessions")
    op.drop_table("learners")
