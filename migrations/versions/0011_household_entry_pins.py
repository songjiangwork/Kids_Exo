"""Add household entry PIN fields.

Revision ID: 0011_household_entry_pins
Revises: 0010_local_auth_households
Create Date: 2026-06-13
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0011_household_entry_pins"
down_revision: str | None = "0010_local_auth_households"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


DEFAULT_PIN_HASH = "pbkdf2_sha256$260000$n5iH2V0Df7LIkQJcNWdq1Q$RpRS__ztusRFmMAbufTlcMWS1rnQXcCfp49mF6QNVWc"


def upgrade() -> None:
    with op.batch_alter_table("household_members") as batch_op:
        batch_op.add_column(sa.Column("parent_unlock_pin_hash", sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column("parent_unlock_pin_updated_at", sa.DateTime(timezone=True), nullable=True))

    with op.batch_alter_table("learners") as batch_op:
        batch_op.add_column(sa.Column("avatar_key", sa.String(length=40), nullable=True))
        batch_op.add_column(sa.Column("student_login_enabled", sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column("student_code", sa.String(length=80), nullable=True))
        batch_op.add_column(sa.Column("student_pin_hash", sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column("student_pin_updated_at", sa.DateTime(timezone=True), nullable=True))
        batch_op.add_column(sa.Column("student_login_failed_count", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("student_login_locked_until", sa.DateTime(timezone=True), nullable=True))

    connection = op.get_bind()
    connection.execute(
        sa.text(
            """
            UPDATE household_members
            SET parent_unlock_pin_hash = :pin_hash,
                parent_unlock_pin_updated_at = CURRENT_TIMESTAMP
            WHERE role IN ('parent', 'admin')
              AND parent_unlock_pin_hash IS NULL
            """
        ),
        {"pin_hash": DEFAULT_PIN_HASH},
    )
    connection.execute(
        sa.text(
            """
            UPDATE learners
            SET avatar_key = 'fox',
                student_login_enabled = 1,
                student_pin_hash = :pin_hash,
                student_pin_updated_at = CURRENT_TIMESTAMP,
                student_login_failed_count = 0
            """
        ),
        {"pin_hash": DEFAULT_PIN_HASH},
    )

    with op.batch_alter_table("learners") as batch_op:
        batch_op.alter_column("avatar_key", existing_type=sa.String(length=40), nullable=False)
        batch_op.alter_column("student_login_enabled", existing_type=sa.Boolean(), nullable=False)
        batch_op.alter_column("student_login_failed_count", existing_type=sa.Integer(), nullable=False)
        batch_op.create_unique_constraint(
            "uq_learners_household_id_student_code",
            ["household_id", "student_code"],
        )


def downgrade() -> None:
    with op.batch_alter_table("learners") as batch_op:
        batch_op.drop_constraint("uq_learners_household_id_student_code", type_="unique")
        batch_op.drop_column("student_login_locked_until")
        batch_op.drop_column("student_login_failed_count")
        batch_op.drop_column("student_pin_updated_at")
        batch_op.drop_column("student_pin_hash")
        batch_op.drop_column("student_code")
        batch_op.drop_column("student_login_enabled")
        batch_op.drop_column("avatar_key")

    with op.batch_alter_table("household_members") as batch_op:
        batch_op.drop_column("parent_unlock_pin_updated_at")
        batch_op.drop_column("parent_unlock_pin_hash")
