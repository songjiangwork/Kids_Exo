"""Add static audio URL metadata to question instances."""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0006_question_audio_url"
down_revision: str | None = "0005_session_subject_skill"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("question_instances") as batch_op:
        batch_op.add_column(sa.Column("audio_url", sa.String(length=300), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("question_instances") as batch_op:
        batch_op.drop_column("audio_url")
