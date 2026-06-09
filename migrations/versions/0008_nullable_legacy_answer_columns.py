"""Allow legacy answer columns to be nullable.

Revision ID: 0008_nullable_legacy_answer_columns
Revises: 0007_generic_evaluation_payloads
Create Date: 2026-06-08
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0008_nullable_legacy_answer_columns"
down_revision: str | None = "0007_generic_evaluation_payloads"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("question_instances") as batch_op:
        batch_op.alter_column(
            "expected_answer",
            existing_type=sa.Integer(),
            nullable=True,
        )
    with op.batch_alter_table("response_attempts") as batch_op:
        batch_op.alter_column(
            "normalized_answer",
            existing_type=sa.Integer(),
            nullable=True,
        )


def downgrade() -> None:
    with op.batch_alter_table("response_attempts") as batch_op:
        batch_op.alter_column(
            "normalized_answer",
            existing_type=sa.Integer(),
            nullable=False,
        )
    with op.batch_alter_table("question_instances") as batch_op:
        batch_op.alter_column(
            "expected_answer",
            existing_type=sa.Integer(),
            nullable=False,
        )
