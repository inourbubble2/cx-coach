"""Conversation routes for accessing stored conversations."""

import uuid

from fastapi import APIRouter, HTTPException
from loguru import logger

from app.domain import Conversation
from app.infrastructure.db.conversation_repository import get_conversation

router = APIRouter(prefix="/api/conversations", tags=["conversations"])


@router.get("/{conversation_id}", response_model=Conversation)
async def get_conversation_endpoint(conversation_id: uuid.UUID) -> Conversation:
    """Get a conversation by ID."""
    logger.info(f"Fetching conversation: {conversation_id}")

    try:
        result = await get_conversation(conversation_id)
        if result is None:
            raise HTTPException(
                status_code=404,
                detail=f"대화를 찾을 수 없습니다: {conversation_id}",
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
        logger.error(f"Failed to get conversation: {e}")
        raise HTTPException(
            status_code=500,
            detail="대화 조회 중 오류가 발생했습니다.",
        ) from e
