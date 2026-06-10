"""Add assignment notebook tables.

Revision ID: 0009_assignment_notebook
Revises: 0008_nullable_legacy_answer_columns
Create Date: 2026-06-09
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0009_assignment_notebook"
down_revision: str | None = "0008_nullable_legacy_answer_columns"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "assignments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("learner_id", sa.Integer(), sa.ForeignKey("learners.id"), nullable=False),
        sa.Column("title", sa.String(length=160), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=False, server_default=""),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="assigned"),
        sa.Column("source_type", sa.String(length=40), nullable=False, server_default="parent_assigned"),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by_role", sa.String(length=30), nullable=False, server_default="parent"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_assignments_learner_status", "assignments", ["learner_id", "status"])
    op.create_table(
        "assignment_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("assignment_id", sa.Integer(), sa.ForeignKey("assignments.id"), nullable=False),
        sa.Column("item_type", sa.String(length=40), nullable=False, server_default="practice_plugin"),
        sa.Column("plugin", sa.String(length=100), nullable=False),
        sa.Column("plugin_settings", sa.JSON(), nullable=False),
        sa.Column("question_count", sa.Integer(), nullable=False),
        sa.Column("feedback_mode", sa.String(length=20), nullable=False, server_default="immediate"),
        sa.Column("show_timer", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("order_index", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("required", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("status", sa.String(length=30), nullable=False, server_default="assigned"),
        sa.Column("linked_session_id", sa.Integer(), sa.ForeignKey("practice_sessions.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_assignment_items_assignment_status", "assignment_items", ["assignment_id", "status"])


def downgrade() -> None:
    op.drop_index("ix_assignment_items_assignment_status", table_name="assignment_items")
    op.drop_table("assignment_items")
    op.drop_index("ix_assignments_learner_status", table_name="assignments")
    op.drop_table("assignments")
