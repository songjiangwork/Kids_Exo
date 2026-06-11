"""Add local account and household tables.

Revision ID: 0010_local_auth_households
Revises: 0009_assignment_notebook
Create Date: 2026-06-10
"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "0010_local_auth_households"
down_revision: str | None = "0009_assignment_notebook"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


DEFAULT_ACCOUNT_EMAIL = "local-parent@example.local"
DEFAULT_ACCOUNT_DISPLAY_NAME = "Local Parent"
DEFAULT_ACCOUNT_PASSWORD_HASH = "disabled$local-dev-placeholder"
DEFAULT_HOUSEHOLD_NAME = "Default Household"


def upgrade() -> None:
    op.create_table(
        "accounts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("display_name", sa.String(length=160), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("email"),
    )
    op.create_index(op.f("ix_accounts_email"), "accounts", ["email"], unique=True)

    op.create_table(
        "households",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("owner_account_id", sa.Integer(), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_table(
        "household_members",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("household_id", sa.Integer(), sa.ForeignKey("households.id"), nullable=False),
        sa.Column("account_id", sa.Integer(), sa.ForeignKey("accounts.id"), nullable=False),
        sa.Column("role", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("household_id", "account_id"),
    )

    op.add_column("learners", sa.Column("household_id", sa.Integer(), nullable=True))
    op.add_column("learners", sa.Column("optional_account_id", sa.Integer(), nullable=True))

    connection = op.get_bind()
    connection.execute(
        sa.text(
            """
            INSERT INTO accounts (email, display_name, password_hash, active)
            VALUES (:email, :display_name, :password_hash, 1)
            """
        ),
        {
            "email": DEFAULT_ACCOUNT_EMAIL,
            "display_name": DEFAULT_ACCOUNT_DISPLAY_NAME,
            "password_hash": DEFAULT_ACCOUNT_PASSWORD_HASH,
        },
    )
    account_id = connection.execute(
        sa.text("SELECT id FROM accounts WHERE email = :email"),
        {"email": DEFAULT_ACCOUNT_EMAIL},
    ).scalar_one()
    connection.execute(
        sa.text(
            """
            INSERT INTO households (name, owner_account_id)
            VALUES (:name, :owner_account_id)
            """
        ),
        {"name": DEFAULT_HOUSEHOLD_NAME, "owner_account_id": account_id},
    )
    household_id = connection.execute(
        sa.text("SELECT id FROM households WHERE name = :name"),
        {"name": DEFAULT_HOUSEHOLD_NAME},
    ).scalar_one()
    connection.execute(
        sa.text(
            """
            INSERT INTO household_members (household_id, account_id, role)
            VALUES (:household_id, :account_id, 'parent')
            """
        ),
        {"household_id": household_id, "account_id": account_id},
    )
    connection.execute(
        sa.text("UPDATE learners SET household_id = :household_id WHERE household_id IS NULL"),
        {"household_id": household_id},
    )

    with op.batch_alter_table("learners") as batch_op:
        batch_op.alter_column("household_id", existing_type=sa.Integer(), nullable=False)
        batch_op.create_foreign_key("fk_learners_household_id_households", "households", ["household_id"], ["id"])
        batch_op.create_foreign_key(
            "fk_learners_optional_account_id_accounts",
            "accounts",
            ["optional_account_id"],
            ["id"],
        )


def downgrade() -> None:
    with op.batch_alter_table("learners") as batch_op:
        batch_op.drop_constraint("fk_learners_optional_account_id_accounts", type_="foreignkey")
        batch_op.drop_constraint("fk_learners_household_id_households", type_="foreignkey")
        batch_op.drop_column("optional_account_id")
        batch_op.drop_column("household_id")
    op.drop_table("household_members")
    op.drop_table("households")
    op.drop_index(op.f("ix_accounts_email"), table_name="accounts")
    op.drop_table("accounts")
