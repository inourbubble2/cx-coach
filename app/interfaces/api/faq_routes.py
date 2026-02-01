"""FastAPI routes for FAQ document management."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, File, HTTPException, Query, UploadFile
from loguru import logger
from pydantic import BaseModel, HttpUrl

from app.application.faq_service import (
    delete_faq,
    get_faq_document,
    list_faq,
    toggle_faq_active,
    update_faq_content,
    upload_faq_document,
    upload_faq_from_url,
    upload_faq_text,
)
from app.domain import FAQListItem, FAQUploadResponse

router = APIRouter(prefix="/api/faq", tags=["faq"])

MAX_FAQ_FILE_SIZE_MB = 10


class FAQListResponse(BaseModel):
    """Response for FAQ list endpoint."""

    items: list[FAQListItem]
    count: int


class FAQToggleRequest(BaseModel):
    """Request body for FAQ toggle endpoint."""

    is_active: bool


class FAQToggleResponse(BaseModel):
    """Response for FAQ toggle endpoint."""

    success: bool
    document_id: str
    is_active: bool


class FAQDeleteResponse(BaseModel):
    """Response for FAQ delete endpoint."""

    deleted: bool
    document_id: str


class FAQUrlUploadRequest(BaseModel):
    """Request body for URL upload endpoint."""

    url: HttpUrl


class FAQTextUploadRequest(BaseModel):
    """Request body for Text upload endpoint."""

    title: str
    content: str


class FAQUpdateRequest(BaseModel):
    """Request body for FAQ update endpoint."""

    content: str


@router.post("/file", response_model=FAQUploadResponse)
async def upload_faq(
    file: Annotated[
        UploadFile,
        File(description="PDF or TXT file containing FAQ content"),
    ],
) -> FAQUploadResponse:
    """Upload a FAQ document for vectorization.

    The document will be processed, chunked, and embedded for
    similarity search during conversation analysis.

    Supported formats:
    - PDF: Text will be extracted from all pages
    - TXT: Plain text file (UTF-8, CP949, EUC-KR supported)

    Maximum file size: 10MB
    """
    logger.info(f"Received FAQ upload request: {file.filename}")

    if not file.filename:
        raise HTTPException(status_code=400, detail="파일명이 필요합니다")

    ext = file.filename.lower().rsplit(".", 1)[-1] if "." in file.filename else ""
    if ext not in ("pdf", "txt", "text"):
        raise HTTPException(
            status_code=400,
            detail="지원하지 않는 파일 형식입니다. PDF 또는 TXT 파일을 사용하세요.",
        )

    content = await file.read()
    file_size_mb = len(content) / (1024 * 1024)

    if file_size_mb > MAX_FAQ_FILE_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"파일 크기가 {MAX_FAQ_FILE_SIZE_MB}MB를 초과합니다: {file_size_mb:.1f}MB",
        )

    try:
        result = await upload_faq_document(content, file.filename)
        return result
    except ValueError as e:
        logger.warning(f"FAQ upload failed with ValueError: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        logger.error(f"FAQ upload failed with RuntimeError: {e}")
        raise HTTPException(status_code=503, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Unexpected error during FAQ upload: {e}")
        raise HTTPException(
            status_code=500,
            detail="FAQ 업로드 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
        ) from e


@router.post("/url", response_model=FAQUploadResponse)
async def upload_faq_from_url_endpoint(
    request: FAQUrlUploadRequest,
) -> FAQUploadResponse:
    """Upload a FAQ document from a URL.

    The content at the URL will be fetched, processed, chunked,
    and embedded for similarity search during conversation analysis.

    Supported content types:
    - text/html: HTML pages (navigation, scripts, styles removed)
    - text/plain: Plain text content
    """
    logger.info(f"Received FAQ URL upload request: {request.url}")

    try:
        result = await upload_faq_from_url(str(request.url))
        return result
    except ValueError as e:
        logger.warning(f"FAQ URL upload failed with ValueError: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        logger.error(f"FAQ URL upload failed with RuntimeError: {e}")
        raise HTTPException(status_code=503, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Unexpected error during FAQ URL upload: {e}")
        raise HTTPException(
            status_code=500,
            detail="URL에서 FAQ 업로드 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
        ) from e


@router.get("/list", response_model=FAQListResponse)
async def list_faq_documents(
    include_inactive: Annotated[bool, Query()] = False,
) -> FAQListResponse:
    """List all FAQ documents.

    Returns a list of uploaded FAQ documents with their metadata.
    By default, only active documents are returned.
    """
    logger.info(f"Listing FAQ documents: include_inactive={include_inactive}")

    try:
        items = await list_faq(include_inactive=include_inactive)
        return FAQListResponse(items=items, count=len(items))
    except RuntimeError as e:
        logger.error(f"Database configuration error: {e}")
        raise HTTPException(
            status_code=503,
            detail="데이터베이스가 설정되지 않았습니다.",
        ) from e
    except Exception as e:
        logger.error(f"Failed to list FAQ documents: {e}")
        raise HTTPException(
            status_code=500,
            detail="FAQ 목록 조회 중 오류가 발생했습니다.",
        ) from e


@router.patch("/{document_id}/status", response_model=FAQToggleResponse)
async def toggle_faq_document(
    document_id: UUID,
    request: FAQToggleRequest,
) -> FAQToggleResponse:
    """Toggle the active status of a FAQ document.

    Active documents are included in similarity search during analysis.
    Inactive documents are excluded but not deleted.
    """
    logger.info(
        f"Toggling FAQ document {document_id} status to is_active={request.is_active}"
    )

    try:
        success = await toggle_faq_active(document_id, request.is_active)

        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"FAQ 문서를 찾을 수 없습니다: {document_id}",
            )

        return FAQToggleResponse(
            success=True,
            document_id=str(document_id),
            is_active=request.is_active,
        )
    except HTTPException:
        raise
    except RuntimeError as e:
        logger.error(f"Database configuration error: {e}")
        raise HTTPException(
            status_code=503,
            detail="데이터베이스가 설정되지 않았습니다.",
        ) from e
    except Exception as e:
        logger.error(f"Failed to toggle FAQ document: {e}")
        raise HTTPException(
            status_code=500,
            detail="FAQ 상태 변경 중 오류가 발생했습니다.",
        ) from e


@router.delete("/{document_id}", response_model=FAQDeleteResponse)
async def delete_faq_document(document_id: UUID) -> FAQDeleteResponse:
    """Delete a FAQ document and all its chunks.

    This operation is irreversible. All associated embeddings
    will be permanently deleted.
    """
    logger.info(f"Deleting FAQ document: {document_id}")

    try:
        deleted = await delete_faq(document_id)

        if not deleted:
            raise HTTPException(
                status_code=404,
                detail=f"FAQ 문서를 찾을 수 없습니다: {document_id}",
            )

        return FAQDeleteResponse(deleted=True, document_id=str(document_id))
    except HTTPException:
        raise
    except RuntimeError as e:
        logger.error(f"Database configuration error: {e}")
        raise HTTPException(
            status_code=503,
            detail="데이터베이스가 설정되지 않았습니다.",
        ) from e
    except Exception as e:
        logger.error(f"Failed to delete FAQ document: {e}")
        raise HTTPException(
            status_code=500,
            detail="FAQ 삭제 중 오류가 발생했습니다.",
        ) from e


@router.post("/text", response_model=FAQUploadResponse)
async def upload_faq_text_endpoint(
    request: FAQTextUploadRequest,
) -> FAQUploadResponse:
    """Upload FAQ content from direct text input."""
    logger.info(f"Received FAQ text upload request: {request.title}")

    try:
        result = await upload_faq_text(request.title, request.content)
        return result
    except ValueError as e:
        logger.warning(f"FAQ text upload failed with ValueError: {e}")
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        logger.error(f"FAQ text upload failed with RuntimeError: {e}")
        raise HTTPException(status_code=503, detail=str(e)) from e
    except Exception as e:
        logger.error(f"Unexpected error during FAQ text upload: {e}")
        raise HTTPException(
            status_code=500,
            detail="텍스트 FAQ 업로드 중 오류가 발생했습니다.",
        ) from e


@router.get("/{document_id}", response_model=FAQListItem)
async def get_faq_detail_endpoint(document_id: UUID) -> FAQListItem:
    """Get FAQ document details including full content."""
    logger.info(f"Fetching FAQ document detail: {document_id}")

    try:
        item = await get_faq_document(document_id)
        if not item:
            raise HTTPException(
                status_code=404,
                detail=f"FAQ 문서를 찾을 수 없습니다: {document_id}",
            )
        return item
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get FAQ detail: {e}")
        raise HTTPException(
            status_code=500,
            detail="FAQ 상세 조회 중 오류가 발생했습니다.",
        ) from e


@router.patch("/{document_id}", response_model=FAQToggleResponse)
async def update_faq_endpoint(
    document_id: UUID,
    request: FAQUpdateRequest,
) -> FAQToggleResponse:
    """Update FAQ document content."""
    logger.info(f"Updating FAQ document content: {document_id}")

    try:
        success = await update_faq_content(document_id, request.content)
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"FAQ 문서를 찾을 수 없습니다: {document_id}",
            )

        # Return boolean success wrapped in response (reusing toggle response for simplicity or define new)
        # Reusing FAQToggleResponse but 'is_active' field might not match semantics perfectly.
        # But for MVP it's okay, or use Generic response.
        # Currently re-embedding keeps 'is_active' state.

        # Let's check current active state to return correct is_active
        doc = await get_faq_document(document_id)
        is_active = doc.is_active if doc else True

        return FAQToggleResponse(
            success=True,
            document_id=str(document_id),
            is_active=is_active,
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail="데이터베이스 오류") from e
    except Exception as e:
        logger.error(f"Failed to update FAQ: {e}")
        raise HTTPException(
            status_code=500,
            detail="FAQ 수정 중 오류가 발생했습니다.",
        ) from e
