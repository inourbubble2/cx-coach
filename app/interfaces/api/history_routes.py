"""History routes for analysis history management."""

from typing import Annotated, Literal

from fastapi import APIRouter, HTTPException, Query
from loguru import logger
from pydantic import BaseModel

from app.domain import (
    AnalysisFeedbackRequest,
    AnalysisHistorySummary,
    AnalysisResult,
    Conversation,
)
from app.infrastructure.db.analysis_repository import (
    delete_analysis,
    get_analysis,
    list_analyses,
    update_analysis_feedback,
)
from app.infrastructure.db.conversation_repository import get_conversation

router = APIRouter(prefix="/api/history", tags=["history"])


class HistoryListResponse(BaseModel):
    """Response for history list endpoint."""

    items: list[AnalysisHistorySummary]
    count: int


class DeleteResponse(BaseModel):
    """Response for delete endpoint."""

    deleted: bool
    request_id: str


@router.get("", response_model=HistoryListResponse)
async def list_history(
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    sort: Annotated[Literal["date", "score"], Query()] = "date",
) -> HistoryListResponse:
    """List analysis history.

    Returns a list of past analysis results sorted by date or score.
    """
    logger.info(f"Listing analysis history: limit={limit}, sort={sort}")

    try:
        items = await list_analyses(limit=limit, sort_by=sort)
        return HistoryListResponse(items=items, count=len(items))
    except RuntimeError as e:
        logger.error(f"Database configuration error: {e}")
        raise HTTPException(
            status_code=503,
            detail="데이터베이스가 설정되지 않았습니다.",
        ) from e
    except Exception as e:
        logger.error(f"Failed to list history: {e}")
        raise HTTPException(
            status_code=500,
            detail="이력 조회 중 오류가 발생했습니다.",
        ) from e


@router.get("/{request_id}", response_model=AnalysisResult)
async def get_history_detail(request_id: str) -> AnalysisResult:
    """Get detailed analysis result by request ID."""
    logger.info(f"Fetching analysis detail: {request_id}")

    try:
        result = await get_analysis(request_id)
        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"분석 결과를 찾을 수 없습니다: {request_id}",
            )
        return result
    except HTTPException:
        raise
    except RuntimeError as e:
        logger.error(f"Database configuration error: {e}")
        raise HTTPException(
            status_code=503,
            detail="데이터베이스가 설정되지 않았습니다.",
        ) from e
    except Exception as e:
        logger.error(f"Failed to get analysis detail: {e}")
        raise HTTPException(
            status_code=500,
            detail="상세 조회 중 오류가 발생했습니다.",
        ) from e


@router.delete("/{request_id}", response_model=DeleteResponse)
async def delete_history(request_id: str) -> DeleteResponse:
    """Delete an analysis result by request ID."""
    logger.info(f"Deleting analysis: {request_id}")

    try:
        deleted = await delete_analysis(request_id)
        if not deleted:
            raise HTTPException(
                status_code=404,
                detail=f"분석 결과를 찾을 수 없습니다: {request_id}",
            )
        return DeleteResponse(deleted=True, request_id=request_id)
    except HTTPException:
        raise
    except RuntimeError as e:
        logger.error(f"Database configuration error: {e}")
        raise HTTPException(
            status_code=503,
            detail="데이터베이스가 설정되지 않았습니다.",
        ) from e
    except Exception as e:
        logger.error(f"Failed to delete analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail="삭제 중 오류가 발생했습니다.",
        ) from e


@router.patch("/{request_id}/feedback")
async def update_feedback_endpoint(
    request_id: str,
    feedback: AnalysisFeedbackRequest,
) -> dict:
    """Update analysis feedback (KPI metrics)."""
    logger.info(f"Updating feedback for: {request_id}")

    try:
        success = await update_analysis_feedback(
            request_id, feedback.is_resolved, feedback.csat_score
        )

        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"분석 결과를 찾을 수 없습니다: {request_id}",
            )

        return {"success": True, "request_id": request_id}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update feedback: {e}")
        raise HTTPException(
            status_code=500,
            detail="피드백 업데이트 중 오류가 발생했습니다.",
        ) from e


@router.get("/{request_id}/conversation", response_model=Conversation)
async def get_analysis_conversation(request_id: str) -> Conversation:
    """Get the conversation associated with an analysis result."""
    logger.info(f"Fetching conversation for analysis: {request_id}")

    try:
        analysis = await get_analysis(request_id)
        if analysis is None:
            raise HTTPException(
                status_code=404,
                detail=f"분석 결과를 찾을 수 없습니다: {request_id}",
            )

        if analysis.conversation_id is None:
            raise HTTPException(
                status_code=404,
                detail=f"이 분석 결과에는 연결된 대화가 없습니다: {request_id}",
            )

        conversation = await get_conversation(analysis.conversation_id)
        if conversation is None:
            raise HTTPException(
                status_code=404,
                detail=f"대화를 찾을 수 없습니다: {analysis.conversation_id}",
            )

        return conversation
    except HTTPException:
        raise
    except RuntimeError as e:
        logger.error(f"Database configuration error: {e}")
        raise HTTPException(
            status_code=503,
            detail="데이터베이스가 설정되지 않았습니다.",
        ) from e
    except Exception as e:
        logger.error(f"Failed to get conversation for analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail="대화 조회 중 오류가 발생했습니다.",
        ) from e
