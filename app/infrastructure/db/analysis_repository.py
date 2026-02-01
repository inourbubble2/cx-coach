"""Database repository for analysis results using SQLAlchemy.

Replaces the Supabase REST client with direct database access.
"""

from typing import Literal

from loguru import logger
from sqlalchemy import delete, select

from app.domain import (
    AnalysisHistorySummary,
    AnalysisResult,
    Improvement,
    Scores,
)
from app.infrastructure.db.database import get_session
from app.infrastructure.db.models.analysis import AnalysisResult as DBAnalysisResult


def _db_to_domain(db_row: DBAnalysisResult) -> AnalysisResult:
    """Convert DB model to Domain model."""
    scores = Scores(
        clarification=db_row.clarification_score,
        empathy_tone=db_row.empathy_tone_score,
        solution_accuracy=db_row.solution_accuracy_score,
        actionability=db_row.actionability_score,
        confirmation_closure=db_row.confirmation_closure_score,
        compliance_safety=db_row.compliance_safety_score,
    )

    improvements = [Improvement(**imp) for imp in db_row.improvements]

    return AnalysisResult(
        request_id=db_row.request_id,
        conversation_id=db_row.conversation_id,
        analyzed_at=db_row.analyzed_at,
        scores=scores,
        total_score=db_row.total_score,
        strengths=db_row.strengths,
        improvements=improvements,
        overall_feedback=db_row.overall_feedback,
        is_resolved=db_row.is_resolved,
        csat_score=db_row.csat_score,
    )


def _domain_to_summary(
    request_id: str, analyzed_at, total_score: int
) -> AnalysisHistorySummary:
    """Convert basic stats to summary."""
    if total_score >= 90:
        grade = "A"
    elif total_score >= 80:
        grade = "B"
    elif total_score >= 70:
        grade = "C"
    elif total_score >= 60:
        grade = "D"
    else:
        grade = "F"

    return AnalysisHistorySummary(
        request_id=request_id,
        analyzed_at=analyzed_at,
        total_score=total_score,
        grade=grade,
    )


async def save_analysis(result: AnalysisResult) -> None:
    """Save an analysis result to the database."""
    logger.debug(f"Saving analysis result: {result.request_id}")

    db_obj = DBAnalysisResult(
        request_id=result.request_id,
        conversation_id=result.conversation_id,
        analyzed_at=result.analyzed_at,
        clarification_score=result.scores.clarification,
        empathy_tone_score=result.scores.empathy_tone,
        solution_accuracy_score=result.scores.solution_accuracy,
        actionability_score=result.scores.actionability,
        confirmation_closure_score=result.scores.confirmation_closure,
        compliance_safety_score=result.scores.compliance_safety,
        total_score=result.total_score,
        strengths=result.strengths,
        improvements=[imp.model_dump() for imp in result.improvements],
        overall_feedback=result.overall_feedback,
        is_resolved=result.is_resolved,
        csat_score=result.csat_score,
    )

    async for session in get_session():
        session.add(db_obj)
        await session.commit()
        break  # distinct session per operation

    logger.info(f"Analysis result saved: {result.request_id}")


async def get_analysis(request_id: str) -> AnalysisResult | None:
    """Retrieve an analysis result by request ID."""
    logger.debug(f"Fetching analysis result: {request_id}")

    query = select(DBAnalysisResult).where(DBAnalysisResult.request_id == request_id)

    async for session in get_session():
        result = await session.execute(query)
        db_obj = result.scalar_one_or_none()
        if db_obj:
            return _db_to_domain(db_obj)
        return None
    return None


async def list_analyses(
    limit: int = 50,
    sort_by: Literal["date", "score"] = "date",
) -> list[AnalysisHistorySummary]:
    """List analysis results with pagination and sorting."""
    logger.debug(f"Listing analyses: limit={limit}, sort_by={sort_by}")

    order_col = (
        DBAnalysisResult.analyzed_at.desc()
        if sort_by == "date"
        else DBAnalysisResult.total_score.desc()
    )
    query = (
        select(
            DBAnalysisResult.request_id,
            DBAnalysisResult.analyzed_at,
            DBAnalysisResult.total_score,
        )
        .order_by(order_col)
        .limit(limit)
    )

    items = []
    async for session in get_session():
        result = await session.execute(query)
        rows = result.all()
        for row in rows:
            items.append(
                _domain_to_summary(row.request_id, row.analyzed_at, row.total_score)
            )
        break

    return items


async def delete_analysis(request_id: str) -> bool:
    """Delete an analysis result by request ID."""
    logger.debug(f"Deleting analysis result: {request_id}")

    query = delete(DBAnalysisResult).where(DBAnalysisResult.request_id == request_id)

    async for session in get_session():
        result = await session.execute(query)
        await session.commit()
        deleted = result.rowcount > 0
        if deleted:
            logger.info(f"Analysis result deleted: {request_id}")
        else:
            logger.debug(f"Analysis result not found for deletion: {request_id}")
        return deleted
    return False


async def update_analysis_feedback(
    request_id: str, is_resolved: bool | None, csat_score: int | None
) -> bool:
    """Update analysis feedback (KPI metrics)."""
    logger.debug(
        f"Updating analysis feedback: {request_id}, resolved={is_resolved}, csat={csat_score}"
    )

    query = select(DBAnalysisResult).where(DBAnalysisResult.request_id == request_id)

    async for session in get_session():
        result = await session.execute(query)
        db_obj = result.scalar_one_or_none()

        if db_obj:
            if is_resolved is not None:
                db_obj.is_resolved = is_resolved
            if csat_score is not None:
                db_obj.csat_score = csat_score

            await session.commit()
            return True
        return False
    return False
