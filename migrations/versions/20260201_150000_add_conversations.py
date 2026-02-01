"""add_conversations

Revision ID: a1b2c3d4e5f6
Revises: 6163adea5b37
Create Date: 2026-02-01 15:00:00.000000+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: str | None = "6163adea5b37"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade database schema."""
    # Create conversations table
    op.create_table(
        "conversations",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column("turn_count", sa.Integer(), nullable=False),
        sa.Column("turns", postgresql.JSONB(), nullable=False),
        sa.Column("metadata", postgresql.JSONB(), nullable=True),
    )
    op.create_index(
        "ix_conversations_created_at",
        "conversations",
        ["created_at"],
    )

    # Add conversation_id FK to analysis_results
    op.add_column(
        "analysis_results",
        sa.Column(
            "conversation_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )
    op.create_foreign_key(
        "fk_analysis_results_conversation_id",
        "analysis_results",
        "conversations",
        ["conversation_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_analysis_results_conversation_id",
        "analysis_results",
        ["conversation_id"],
    )


def downgrade() -> None:
    """Downgrade database schema."""
    # Remove FK and column from analysis_results
    op.drop_index("ix_analysis_results_conversation_id", table_name="analysis_results")
    op.drop_constraint(
        "fk_analysis_results_conversation_id",
        "analysis_results",
        type_="foreignkey",
    )
    op.drop_column("analysis_results", "conversation_id")

    # Drop conversations table
    op.drop_index("ix_conversations_created_at", table_name="conversations")
    op.drop_table("conversations")
