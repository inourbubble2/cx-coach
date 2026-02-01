from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from pydantic import BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.database import get_session
from app.infrastructure.db.models.analysis import AnalysisResult

router = APIRouter(prefix="/api/home", tags=["home"])


class DashboardStats(BaseModel):
    total_analyzed: int
    avg_score: float
    resolution_rate: float
    avg_analysis_seconds: float = 0.0


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    session: AsyncSession = Depends(get_session),
) -> DashboardStats:
    """Get aggregated statistics for the dashboard."""
    try:
        # Total Analyzed
        total_count = await session.scalar(
            select(func.count(AnalysisResult.request_id))
        )

        # Avg Score
        avg_score = await session.scalar(select(func.avg(AnalysisResult.total_score)))

        # Resolution Rate
        resolved_count = await session.scalar(
            select(func.count(AnalysisResult.request_id)).where(
                AnalysisResult.is_resolved == True
            )
        )

        resolution_rate = 0.0
        if total_count and total_count > 0:
            resolution_rate = round((resolved_count / total_count) * 100, 1)

        # Mock Analysis Time (approx 3-5 seconds usually)
        # TODO: Calculate real time diff between upload and analysis completion
        avg_analysis_seconds = 4.2

        return DashboardStats(
            total_analyzed=total_count or 0,
            avg_score=round(avg_score or 0.0, 1),
            resolution_rate=resolution_rate,
            avg_analysis_seconds=avg_analysis_seconds,
        )
    except Exception as e:
        logger.error(f"Failed to fetch dashboard stats: {e}")
        raise HTTPException(status_code=500, detail="Stats calculation failed")
