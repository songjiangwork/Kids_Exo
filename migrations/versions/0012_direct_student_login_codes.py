"""Add public household codes for direct student login.

Revision ID: 0012_direct_student_login_codes
Revises: 0011_household_entry_pins
Create Date: 2026-06-14
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0012_direct_student_login_codes"
down_revision: str | None = "0011_household_entry_pins"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


PUBLIC_CODE_ALPHABET = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"


def upgrade() -> None:
    with op.batch_alter_table("households") as batch_op:
        batch_op.add_column(sa.Column("household_code", sa.String(length=20), nullable=True))

    connection = op.get_bind()
    household_ids = list(connection.execute(sa.text("SELECT id FROM households ORDER BY id")).scalars())
    for offset, household_id in enumerate(household_ids, start=1):
        connection.execute(
            sa.text("UPDATE households SET household_code = :code WHERE id = :id"),
            {"code": _code_from_number(offset), "id": household_id},
        )

    learners = connection.execute(
        sa.text(
            """
            SELECT id, household_id
            FROM learners
            WHERE student_code IS NULL OR student_code = ''
            ORDER BY household_id, id
            """
        )
    ).mappings()
    household_counts: dict[int, int] = {}
    for learner in learners:
        household_id = int(learner["household_id"])
        household_counts[household_id] = household_counts.get(household_id, 0) + 1
        connection.execute(
            sa.text("UPDATE learners SET student_code = :code WHERE id = :id"),
            {
                "code": f"S{household_counts[household_id]}",
                "id": learner["id"],
            },
        )

    with op.batch_alter_table("households") as batch_op:
        batch_op.alter_column("household_code", existing_type=sa.String(length=20), nullable=False)
        batch_op.create_unique_constraint("uq_households_household_code", ["household_code"])


def downgrade() -> None:
    with op.batch_alter_table("households") as batch_op:
        batch_op.drop_constraint("uq_households_household_code", type_="unique")
        batch_op.drop_column("household_code")


def _code_from_number(value: int) -> str:
    base = len(PUBLIC_CODE_ALPHABET)
    digits: list[str] = []
    current = value
    while current:
        current, remainder = divmod(current, base)
        digits.append(PUBLIC_CODE_ALPHABET[remainder])
    return ("K" + "".join(reversed(digits))).ljust(6, "2")
