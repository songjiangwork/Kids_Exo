"""Add online question interaction metadata."""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0004_question_interaction_metadata"
down_revision: str | None = "0003_active_practice_time"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("question_instances") as batch_op:
        batch_op.add_column(
            sa.Column(
                "question_type",
                sa.String(length=30),
                server_default="numeric",
                nullable=False,
            )
        )
        batch_op.add_column(
            sa.Column(
                "choices",
                sa.JSON(),
                server_default="[]",
                nullable=False,
            )
        )
        batch_op.add_column(sa.Column("speech_text", sa.String(length=300), nullable=True))
        batch_op.add_column(sa.Column("speech_locale", sa.String(length=20), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("question_instances") as batch_op:
        batch_op.drop_column("speech_locale")
        batch_op.drop_column("speech_text")
        batch_op.drop_column("choices")
        batch_op.drop_column("question_type")
