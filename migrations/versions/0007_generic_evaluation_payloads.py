"""Add generic evaluation payload columns."""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0007_generic_evaluation_payloads"
down_revision: str | None = "0006_question_audio_url"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("question_instances") as batch_op:
        batch_op.add_column(
            sa.Column(
                "renderer_type",
                sa.String(length=80),
                server_default="numeric_answer",
                nullable=False,
            )
        )
        batch_op.add_column(
            sa.Column(
                "answer_type",
                sa.String(length=80),
                server_default="integer_exact",
                nullable=False,
            )
        )
        batch_op.add_column(
            sa.Column(
                "evaluation_payload",
                sa.JSON(),
                server_default="{}",
                nullable=False,
            )
        )
        batch_op.add_column(
            sa.Column(
                "prompt_payload",
                sa.JSON(),
                server_default="{}",
                nullable=False,
            )
        )
        batch_op.add_column(
            sa.Column(
                "public_payload",
                sa.JSON(),
                server_default="{}",
                nullable=False,
            )
        )

    with op.batch_alter_table("response_attempts") as batch_op:
        batch_op.add_column(sa.Column("submitted_payload", sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column("normalized_payload", sa.JSON(), nullable=True))
        batch_op.add_column(
            sa.Column(
                "evaluation_detail",
                sa.JSON(),
                server_default="{}",
                nullable=False,
            )
        )


def downgrade() -> None:
    with op.batch_alter_table("response_attempts") as batch_op:
        batch_op.drop_column("evaluation_detail")
        batch_op.drop_column("normalized_payload")
        batch_op.drop_column("submitted_payload")

    with op.batch_alter_table("question_instances") as batch_op:
        batch_op.drop_column("public_payload")
        batch_op.drop_column("prompt_payload")
        batch_op.drop_column("evaluation_payload")
        batch_op.drop_column("answer_type")
        batch_op.drop_column("renderer_type")
