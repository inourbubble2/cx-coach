"""SQLAlchemy model for analysis results."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.db.models.base import Base


class AnalysisResult(Base):
    """Analysis result table for storing counseling analysis."""

    __tablename__ = "analysis_results"

    request_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    analyzed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )

    # Individual scores (1-10)
    clarification_score: Mapped[int] = mapped_column(Integer, nullable=False)
    empathy_tone_score: Mapped[int] = mapped_column(Integer, nullable=False)
    solution_accuracy_score: Mapped[int] = mapped_column(Integer, nullable=False)
    actionability_score: Mapped[int] = mapped_column(Integer, nullable=False)
    confirmation_closure_score: Mapped[int] = mapped_column(Integer, nullable=False)
    compliance_safety_score: Mapped[int] = mapped_column(Integer, nullable=False)

    # Total score (0-100)
    total_score: Mapped[int] = mapped_column(Integer, nullable=False)

    # Feedback arrays/objects
    strengths: Mapped[list[str]] = mapped_column(ARRAY(Text), nullable=False)
    improvements: Mapped[list[dict]] = mapped_column(JSONB, nullable=False)
    overall_feedback: Mapped[str] = mapped_column(Text, nullable=False)

    # KPI Fields
    is_resolved: Mapped[bool] = mapped_column(Boolean, nullable=True)
    csat_score: Mapped[int] = mapped_column(Integer, nullable=True)
