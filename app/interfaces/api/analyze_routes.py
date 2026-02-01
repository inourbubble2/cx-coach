"""Analysis routes for conversation analysis."""

from typing import Annotated

from fastapi import APIRouter, File, HTTPException, UploadFile
from loguru import logger
from pydantic import BaseModel

from app.application.analysis_agent.nodes.guardrail import ConversationGuardrailError
from app.domain import AnalysisResult

router = APIRouter(prefix="/api/analyze", tags=["analyze"])

MAX_FILE_SIZE_MB = 25


class TextAnalysisRequest(BaseModel):
    """Request body for text-based analysis."""

    text: str


@router.post("/text", response_model=AnalysisResult)
async def analyze_text_endpoint(request: TextAnalysisRequest) -> AnalysisResult:
    """Analyze a conversation from plain text.

    The text should contain conversation turns in one of the supported formats:
    - "상담원: 메시지" / "고객: 메시지"
    - "[Agent] 메시지" / "[Customer] 메시지"
    - "Agent: 메시지" / "Customer: 메시지"

    Returns analysis results with scores, strengths, improvements, and feedback.

    Raises:
        400: If content is not a valid customer service consultation
    """
    logger.info("Received text analysis request")

    try:
        from app.application.analysis_service import analyze_conversation
        from app.application.conversation_service import create_from_text

        conversation = await create_from_text(request.text)
        result = await analyze_conversation(conversation)
        return result
    except ConversationGuardrailError as e:
        logger.warning(f"Guardrail rejected content: {e.reason}")
        raise HTTPException(
            status_code=400,
            detail=f"분석할 수 없는 내용입니다: {e.reason}",
        ) from e
    except ValueError as e:
        logger.warning(f"Analysis failed with ValueError: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Unexpected error during analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail="분석 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
        ) from e


@router.post("/file", response_model=AnalysisResult)
async def analyze_file_endpoint(
    file: Annotated[
        UploadFile,
        File(description="TXT, CSV, JSON, or audio file (MP3, WAV, M4A, MP4, WebM)"),
    ],
) -> AnalysisResult:
    """Analyze a conversation from an uploaded file.

    Supported formats:
    - TXT: Plain text with conversation turns
    - CSV: With columns 'speaker' and 'message'
    - JSON: With 'turns' array containing objects with 'speaker' and 'message'
    - Audio: MP3, WAV, M4A, MP4, WebM (transcribed via Whisper API)

    Returns analysis results with scores, strengths, improvements, and feedback.

    Raises:
        400: If content is not a valid customer service consultation
    """
    logger.info(f"Received file analysis request: {file.filename}")

    if not file.filename:
        raise HTTPException(status_code=400, detail="파일명이 필요합니다")

    content = await file.read()
    file_size_mb = len(content) / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"파일 크기가 {MAX_FILE_SIZE_MB}MB를 초과합니다: {file_size_mb:.1f}MB",
        )

    try:
        from app.application.analysis_service import analyze_conversation
        from app.application.conversation_service import create_from_file

        conversation = await create_from_file(content, file.filename)
        result = await analyze_conversation(conversation)
        return result
    except ConversationGuardrailError as e:
        logger.warning(f"Guardrail rejected content: {e.reason}")
        raise HTTPException(
            status_code=400,
            detail=f"분석할 수 없는 내용입니다: {e.reason}",
        ) from e
    except ValueError as e:
        logger.warning(f"File analysis failed with ValueError: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Unexpected error during file analysis: {e}")
        raise HTTPException(
            status_code=500,
            detail="분석 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
        ) from e
