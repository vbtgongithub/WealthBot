"""initial tables users transactions

Revision ID: 0001
Revises:
Create Date: 2026-03-05 00:00:00.000000+00:00
"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=False),
            nullable=False,
            comment="Unique user identifier (UUID)",
        ),
        sa.Column(
            "email",
            sa.String(length=255),
            nullable=False,
            comment="User email address (unique)",
        ),
        sa.Column(
            "email_hash",
            sa.String(length=64),
            nullable=True,
            comment="SHA-256 hash of email for lookups without exposing PII",
        ),
        sa.Column(
            "hashed_password",
            sa.String(length=255),
            nullable=False,
            comment="Bcrypt hashed password",
        ),
        sa.Column(
            "first_name",
            sa.String(length=100),
            nullable=True,
            comment="User first name",
        ),
        sa.Column(
            "last_name",
            sa.String(length=100),
            nullable=True,
            comment="User last name",
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            comment="Whether user account is active",
        ),
        sa.Column(
            "is_verified",
            sa.Boolean(),
            nullable=False,
            comment="Whether email is verified",
        ),
        sa.Column(
            "is_superuser",
            sa.Boolean(),
            nullable=False,
            comment="Whether user has admin privileges",
        ),
        sa.Column(
            "monthly_income",
            sa.Numeric(precision=15, scale=2),
            nullable=True,
            comment="User's monthly income for budgeting",
        ),
        sa.Column(
            "savings_goal",
            sa.Numeric(precision=15, scale=2),
            nullable=True,
            comment="User's monthly savings goal",
        ),
        sa.Column(
            "currency",
            sa.String(length=3),
            nullable=False,
            comment="User's preferred currency (ISO 4217)",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Account creation timestamp",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Last update timestamp",
        ),
        sa.Column(
            "last_login_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="Last login timestamp",
        ),
        sa.Column(
            "data_consent_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="Timestamp when user consented to data processing",
        ),
        sa.Column(
            "deletion_requested_at",
            sa.DateTime(timezone=True),
            nullable=True,
            comment="Timestamp when user requested account deletion",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_email_hash", "users", ["email_hash"])
    op.create_index("ix_users_created_at", "users", ["created_at"])

    op.create_table(
        "transactions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=False),
            nullable=False,
            comment="Unique transaction identifier (UUID)",
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=False),
            nullable=False,
            comment="Reference to user who owns this transaction",
        ),
        sa.Column(
            "amount",
            sa.Numeric(precision=15, scale=2),
            nullable=False,
            comment="Transaction amount with 2 decimal precision",
        ),
        sa.Column(
            "currency",
            sa.String(length=3),
            nullable=False,
            comment="Transaction currency (ISO 4217)",
        ),
        sa.Column(
            "transaction_type",
            sa.String(length=20),
            nullable=False,
            comment="Type: income, expense, transfer, refund",
        ),
        sa.Column(
            "category",
            sa.String(length=50),
            nullable=False,
            comment="Transaction category for budgeting",
        ),
        sa.Column(
            "description",
            sa.String(length=500),
            nullable=True,
            comment="Transaction description",
        ),
        sa.Column(
            "merchant_name",
            sa.String(length=255),
            nullable=True,
            comment="Merchant or payee name",
        ),
        sa.Column("notes", sa.Text(), nullable=True, comment="Additional user notes"),
        sa.Column(
            "predicted_category",
            sa.String(length=50),
            nullable=True,
            comment="ML-predicted category (DistilBERT)",
        ),
        sa.Column(
            "category_confidence",
            sa.Numeric(precision=5, scale=4),
            nullable=True,
            comment="Confidence score for predicted category (0-1)",
        ),
        sa.Column(
            "is_recurring",
            sa.Boolean(),
            nullable=False,
            comment="Whether transaction is recurring",
        ),
        sa.Column(
            "transaction_date",
            sa.DateTime(timezone=True),
            nullable=False,
            comment="Date when transaction occurred",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Record creation timestamp",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
            comment="Last update timestamp",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_transactions_user_id", "transactions", ["user_id"])
    op.create_index("ix_transactions_category", "transactions", ["category"])
    op.create_index(
        "ix_transactions_transaction_date", "transactions", ["transaction_date"]
    )
    op.create_index(
        "ix_transactions_user_date",
        "transactions",
        ["user_id", "transaction_date"],
    )
    op.create_index(
        "ix_transactions_user_category",
        "transactions",
        ["user_id", "category"],
    )
    op.create_index(
        "ix_transactions_date_type",
        "transactions",
        ["transaction_date", "transaction_type"],
    )


def downgrade() -> None:
    op.drop_table("transactions")
    op.drop_table("users")
