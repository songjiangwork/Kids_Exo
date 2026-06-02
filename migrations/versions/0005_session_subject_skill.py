"""Add subject and skill snapshots to practice sessions."""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0005_session_subject_skill"
down_revision: str | None = "0004_question_interaction_metadata"
branch_labels: Sequence[str] | None = None
depends_on: Sequence[str] | None = None


PLUGIN_METADATA = {
    "multiply_by_11": ("Math", "Mental Multiplication", "Multiply by 11"),
    "integer_multiplication_distributive": (
        "Math",
        "Mental Multiplication",
        "Distributive Property Multiplication",
    ),
    "same_tens_ones_sum_to_ten": (
        "Math",
        "Mental Multiplication",
        "Same Tens, Ones Sum to 10",
    ),
    "square_ending_in_5": ("Math", "Mental Multiplication", "Squares Ending in 5"),
    "multiply_by_9_99_999": ("Math", "Mental Multiplication", "Multiply by 9, 99, and 999"),
    "multiply_by_5_25_125": ("Math", "Mental Multiplication", "Multiply by 5, 25, and 125"),
    "three_digit_same_prefix_ones_sum_to_ten": (
        "Math",
        "Mental Multiplication",
        "Three-Digit Same Prefix, Ones Sum to 10",
    ),
    "tens_sum_to_ten_same_ones": (
        "Math",
        "Mental Multiplication",
        "Tens Sum to 10, Same Ones",
    ),
    "near_round_pair_multiplication": (
        "Math",
        "Mental Multiplication",
        "Near Round-Number Pair Multiplication",
    ),
    "difference_of_squares": ("Math", "Mental Multiplication", "Difference of Squares"),
    "french_alphabet_sounds": ("French", "Pronunciation", "French Alphabet Sounds"),
}


def upgrade() -> None:
    with op.batch_alter_table("practice_sessions") as batch_op:
        batch_op.add_column(
            sa.Column("subject", sa.String(length=80), server_default="General", nullable=False)
        )
        batch_op.add_column(
            sa.Column("category", sa.String(length=120), server_default="Practice", nullable=False)
        )
        batch_op.add_column(
            sa.Column("skill", sa.String(length=160), server_default="", nullable=False)
        )

    practice_sessions = sa.table(
        "practice_sessions",
        sa.column("plugin", sa.String(length=100)),
        sa.column("subject", sa.String(length=80)),
        sa.column("category", sa.String(length=120)),
        sa.column("skill", sa.String(length=160)),
    )
    for plugin, (subject, category, skill) in PLUGIN_METADATA.items():
        op.execute(
            practice_sessions.update()
            .where(practice_sessions.c.plugin == plugin)
            .values(subject=subject, category=category, skill=skill)
        )
    op.execute(
        practice_sessions.update()
        .where(practice_sessions.c.skill == "")
        .values(skill=practice_sessions.c.plugin)
    )


def downgrade() -> None:
    with op.batch_alter_table("practice_sessions") as batch_op:
        batch_op.drop_column("skill")
        batch_op.drop_column("category")
        batch_op.drop_column("subject")
