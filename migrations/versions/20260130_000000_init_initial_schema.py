"""Initial schema with analysis_results, faq_documents, faq_chunks tables.

Revision ID: init
Revises:
Create Date: 2026-01-30 00:00:00.000000+00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = "init"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade database schema."""
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Create analysis_results table
    op.create_table(
        "analysis_results",
        sa.Column("request_id", sa.String(36), primary_key=True),
        sa.Column("analyzed_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("greeting_score", sa.Integer(), nullable=False),
        sa.Column("listening_score", sa.Integer(), nullable=False),
        sa.Column("understanding_score", sa.Integer(), nullable=False),
        sa.Column("solution_score", sa.Integer(), nullable=False),
        sa.Column("closing_score", sa.Integer(), nullable=False),
        sa.Column("total_score", sa.Integer(), nullable=False),
        sa.Column("strengths", sa.ARRAY(sa.Text()), nullable=False),
        sa.Column("improvements", sa.dialects.postgresql.JSONB(), nullable=False),
        sa.Column("overall_feedback", sa.Text(), nullable=False),
    )

    # Create index on analyzed_at for sorting
    op.create_index(
        "ix_analysis_results_analyzed_at",
        "analysis_results",
        ["analyzed_at"],
        postgresql_using="btree",
    )

    # Create faq_documents table
    op.create_table(
        "faq_documents",
        sa.Column(
            "id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("filename", sa.String(255), nullable=False),
        sa.Column("file_type", sa.String(10), nullable=False),
        sa.Column("file_size_bytes", sa.Integer(), nullable=False),
        sa.Column("chunk_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "metadata",
            sa.dialects.postgresql.JSONB(),
            nullable=False,
            server_default="{}",
        ),
    )

    # Create faq_chunks table
    op.create_table(
        "faq_chunks",
        sa.Column(
            "id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "document_id",
            sa.dialects.postgresql.UUID(as_uuid=True),
            sa.ForeignKey("faq_documents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(1536), nullable=False),
        sa.Column("token_count", sa.Integer(), nullable=True),
    )

    # Create index on faq_chunks for document lookup
    op.create_index(
        "ix_faq_chunks_document_id",
        "faq_chunks",
        ["document_id"],
        postgresql_using="btree",
    )

    # Create vector similarity index using HNSW (better for larger datasets)
    op.execute(
        """
        CREATE INDEX ix_faq_chunks_embedding
        ON faq_chunks
        USING hnsw (embedding vector_cosine_ops)
        WITH (m = 16, ef_construction = 64)
        """
    )

    # Create search function for FAQ chunks
    op.execute(
        """
        CREATE OR REPLACE FUNCTION search_faq_chunks(
            query_embedding vector(1536),
            match_count int DEFAULT 5,
            match_threshold float DEFAULT 0.7
        )
        RETURNS TABLE (
            chunk_id uuid,
            document_id uuid,
            content text,
            similarity float,
            filename varchar(255),
            token_count int
        )
        LANGUAGE sql STABLE
        AS $$
            SELECT
                c.id AS chunk_id,
                c.document_id,
                c.content,
                1 - (c.embedding <=> query_embedding) AS similarity,
                d.filename,
                c.token_count
            FROM faq_chunks c
            JOIN faq_documents d ON c.document_id = d.id
            WHERE d.is_active = true
            AND 1 - (c.embedding <=> query_embedding) > match_threshold
            ORDER BY c.embedding <=> query_embedding
            LIMIT match_count;
        $$;
        """
    )


def downgrade() -> None:
    """Downgrade database schema."""
    # Drop function
    op.execute("DROP FUNCTION IF EXISTS search_faq_chunks")

    # Drop tables (cascade will handle faq_chunks -> faq_documents FK)
    op.drop_table("faq_chunks")
    op.drop_table("faq_documents")
    op.drop_table("analysis_results")

    # Note: We don't drop the vector extension as it might be used by other schemas
