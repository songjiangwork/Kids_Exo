"""Track active practice time."""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0003_active_practice_time"
down_revision: str | None = "0002_session_timing"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("practice_sessions") as batch_op:
        batch_op.add_column(
            sa.Column(
                "active_elapsed_seconds",
                sa.Integer(),
                server_default="0",
                nullable=False,
            )
        )
        batch_op.add_column(sa.Column("timer_started_at", sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column("last_answered_at", sa.DateTime(timezone=True), nullable=True))
    with op.batch_alter_table("response_attempts") as batch_op:
        batch_op.add_column(
            sa.Column(
                "submitted_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            )
        )


def downgrade() -> None:
    with op.batch_alter_table("response_attempts") as batch_op:
        batch_op.drop_column("submitted_at")
    with op.batch_alter_table("practice_sessions") as batch_op:
        batch_op.drop_column("last_answered_at")
        batch_op.drop_column("timer_started_at")
        batch_op.drop_column("active_elapsed_seconds")
