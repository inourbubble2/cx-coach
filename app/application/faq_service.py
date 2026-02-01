"""FAQ service for document upload, processing, and search.

This service handles FAQ document lifecycle: upload, chunking,
embedding, and similarity search for analysis context.
"""

import ipaddress
import socket
from io import BytesIO
from urllib.parse import urlparse
from uuid import UUID

import httpx
from bs4 import BeautifulSoup
from langchain_core.documents import Document
from langchain_text_splitters import TokenTextSplitter
from loguru import logger
from pypdf import PdfReader

from app.core.config import settings
from app.domain import FAQContext, FAQListItem, FAQSearchResult, FAQUploadResponse
from app.infrastructure.db import (
    create_faq_document,
    delete_faq_document,
    list_faq_documents,
)
from app.infrastructure.db.faq_query_repository import (
    delete_document_by_metadata,
    update_document_active_status,
)
from app.infrastructure.vector_store import (
    add_documents,
    similarity_search,
)

DEFAULT_CHUNK_SIZE = settings.FAQ_CHUNK_SIZE
DEFAULT_CHUNK_OVERLAP = settings.FAQ_CHUNK_OVERLAP


def _extract_text_from_pdf(content: bytes) -> str:
    """Extract text content from a PDF file.

    Args:
        content: PDF file content as bytes

    Returns:
        Extracted text content

    Raises:
        ValueError: If PDF cannot be parsed
    """
    reader = PdfReader(BytesIO(content))
    text_parts = []

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text_parts.append(page_text.strip())

    full_text = "\n\n".join(text_parts)

    if not full_text.strip():
        raise ValueError("PDF에서 텍스트를 추출할 수 없습니다")

    logger.debug(f"Extracted {len(full_text)} characters from PDF")
    return full_text


def _extract_text_from_txt(content: bytes) -> str:
    """Extract text content from a TXT file.

    Args:
        content: TXT file content as bytes

    Returns:
        Decoded text content

    Raises:
        ValueError: If file cannot be decoded
    """
    encodings = ["utf-8", "cp949", "euc-kr", "latin-1"]

    for encoding in encodings:
        try:
            text = content.decode(encoding)
            logger.debug(f"Decoded TXT with {encoding}")
            return text
        except UnicodeDecodeError:
            continue

    raise ValueError(
        "텍스트 파일을 디코딩할 수 없습니다. "
        "UTF-8, CP949, EUC-KR 인코딩을 시도했습니다."
    )


def _chunk_text(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[str]:
    """Split text into overlapping chunks.

    Uses LangChain's TokenTextSplitter for token-aware splitting.

    Args:
        text: Text to chunk
        chunk_size: Target chunk size in characters
        overlap: Number of overlapping characters between chunks

    Returns:
        List of text chunks
    """
    text_splitter = TokenTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
    )

    chunks = text_splitter.split_text(text)
    logger.debug(f"Created {len(chunks)} chunks from {len(text)} characters")
    return chunks


async def _store_faq_chunks(
    chunks: list[str],
    filename: str,
    file_type: str,
    file_size_bytes: int,
    full_text: str,
    url: str | None = None,
    message: str = "FAQ 문서가 성공적으로 업로드되었습니다.",
) -> FAQUploadResponse:
    """Store FAQ chunks in database and vector store.

    Handles the common logic of creating DB record and storing embeddings
    with proper rollback on failure.

    Args:
        chunks: List of text chunks
        filename: Document filename
        file_type: Type of document (pdf, txt, url)
        file_size_bytes: Size of original content
        full_text: Full text content for preview
        url: Optional URL source
        message: Success message for response

    Returns:
        FAQUploadResponse with document info and stats
    """
    faq_doc = await create_faq_document(
        filename=filename,
        file_type=file_type,
        file_size_bytes=file_size_bytes,
        url=url,
        content=full_text,
    )
    document_id = str(faq_doc.id)
    created_at = faq_doc.created_at

    try:
        # Prepare chunks with metadata
        documents = []
        for i, chunk in enumerate(chunks):
            metadata = {
                "document_id": document_id,
                "filename": filename,
                "chunk_index": i,
                "created_at": created_at.isoformat() if created_at else None,
                "is_active": True,
                "file_type": file_type,
                "file_size_bytes": file_size_bytes,
            }
            if url:
                metadata["url"] = url
            documents.append(Document(page_content=chunk, metadata=metadata))

        # Add chunks to Vector Store
        ids = await add_documents(documents)
        chunks_created = len(ids)

        logger.info(
            f"FAQ uploaded successfully: {document_id} ({chunks_created} chunks)"
        )

        return FAQUploadResponse(
            document=faq_doc,
            chunks_created=chunks_created,
            message=message,
        )
    except Exception as e:
        # Rollback: delete orphaned DB record
        logger.warning(
            f"Vector store failed ({e}), rolling back DB record: {faq_doc.id}"
        )
        try:
            await delete_faq_document(faq_doc.id)
        except Exception as rollback_error:
            logger.error(f"Rollback failed: {rollback_error}")
        raise


async def upload_faq_document(
    content: bytes,
    filename: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> FAQUploadResponse:
    """Upload and process a FAQ document.

    Extracts text, chunks it, generates embeddings, and stores
    everything in the database.

    Args:
        content: File content as bytes
        filename: Original filename
        chunk_size: Target chunk size in characters
        chunk_overlap: Overlap between chunks

    Returns:
        FAQUploadResponse with document info and stats

    Raises:
        ValueError: If file type is unsupported or processing fails
    """
    logger.info(f"Uploading FAQ document: {filename}")

    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""

    if ext == "pdf":
        text = _extract_text_from_pdf(content)
        file_type = "pdf"
    elif ext in ("txt", "text"):
        text = _extract_text_from_txt(content)
        file_type = "txt"
    else:
        raise ValueError(
            f"지원하지 않는 파일 형식입니다: {ext}. PDF 또는 TXT 파일을 사용하세요."
        )

    chunks = _chunk_text(text, chunk_size, chunk_overlap)
    return await _store_faq_chunks(
        chunks=chunks,
        filename=filename,
        file_type=file_type,
        file_size_bytes=len(content),
        full_text=text,
    )


async def search_faq(
    query: str,
    limit: int = 5,
    threshold: float = 0.3,
) -> FAQContext:
    """Search FAQ documents for relevant content.

    Args:
        query: Search query text
        limit: Maximum number of results
        threshold: Minimum similarity threshold (0-1)

    Returns:
        FAQContext with search results
    """
    logger.info(f"Searching FAQ for: {query[:50]}...")
    logger.debug(f"Threshold: {threshold}")

    results_scs = await similarity_search(query, k=limit)

    # Filter by threshold manually since asimilarity_search_with_relevance_scores already sorts
    # But we want to enforce pure threshold cutoff if needed.
    # Note: cosine similarity score in langchain-postgres might need normalization check.
    # Assuming score is 0-1 similarity.

    faq_results = []
    for doc, score in results_scs:
        logger.info(f"FAQ Candidate: {doc.metadata.get('filename')} (Score: {score:.4f})")
        
        # if score < threshold:
        #     logger.debug(f"Skipping document due to low score: {score:.4f} < {threshold}")
        #     continue

        metadata = doc.metadata

        # Handle UUID conversion (may already be UUID object from asyncpg)
        chunk_id_raw = metadata.get("chunk_id")
        document_id_raw = metadata.get("document_id")

        chunk_id = UUID(str(chunk_id_raw)) if chunk_id_raw else None
        document_id = UUID(str(document_id_raw)) if document_id_raw else None

        faq_results.append(
            FAQSearchResult(
                chunk_id=chunk_id,
                document_id=document_id,
                content=doc.page_content,
                similarity_score=score,
                filename=metadata.get("filename"),
                token_count=metadata.get("token_count"),
            )
        )

    logger.info(f"FAQ search returned {len(faq_results)} results")

    return FAQContext(results=faq_results)


async def list_faq(include_inactive: bool = False) -> list[FAQListItem]:
    """List all FAQ documents.

    Args:
        include_inactive: Include inactive documents

    Returns:
        List of FAQ documents
    """
    return await list_faq_documents(include_inactive=include_inactive)


async def delete_faq(document_id: UUID) -> bool:
    """Delete a FAQ document and its chunks.

    Args:
        document_id: Document UUID to delete

    Returns:
        True if deleted, False if not found
    """
    deleted_db = await delete_faq_document(document_id)
    deleted_vector = await delete_document_by_metadata(document_id)

    return deleted_db


async def toggle_faq_active(document_id: UUID, is_active: bool) -> bool:
    """Toggle the active status of a FAQ document.

    Args:
        document_id: Document UUID
        is_active: New active status

    Returns:
        True if updated successfully
    """
    logger.info(f"Toggling FAQ {document_id} active status to {is_active}")
    
    # 1. Update Embeddings (for Search)
    embeddings_updated = await update_document_active_status(document_id, is_active)
    
    # 2. Update Document Record (for List/UI)
    from app.infrastructure.db import update_faq_document_active_status
    doc_updated = await update_faq_document_active_status(document_id, is_active)
    
    return doc_updated or embeddings_updated


async def get_faq_document(document_id: UUID):
    """Get FAQ document details including content.

    Args:
        document_id: Document UUID

    Returns:
        FAQ document details
    """
    # This imports lazily to avoid circular imports if any,
    # but strictly speaking we might need a DB accessor for getting single doc by ID.
    # Currently we only have list_faq_documents.
    # We should reuse list_faq_documents filtering by ID or add get_faq_document in DB layer.
    # For MVP, we can filter from list.

    docs = await list_faq_documents(include_inactive=True)
    for doc in docs:
        if str(doc.id) == str(document_id):
            return doc
    return None


async def update_faq_content(
    document_id: UUID,
    content: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> bool:
    """Update FAQ document content and re-embed.

    Args:
        document_id: Document UUID
        content: New content

    Returns:
        True if successful
    """
    logger.info(f"Updating FAQ document {document_id}")

    # 1. Get existing document metadata
    doc = await get_faq_document(document_id)
    if not doc:
        return False

    filename = doc.filename or "updated.txt"
    file_type = doc.file_type or "txt"
    url = doc.url

    # 2. Chunk new content
    chunks = _chunk_text(content, chunk_size, chunk_overlap)

    if not chunks:
        raise ValueError("유효한 내용이 없습니다")

    # 3. Transactional update:
    #    - Delete old vector chunks
    #    - Update DB record (content, size)
    #    - Insert new vector chunks
    # NOTE: Ideally this should be in a DB transaction context.
    # For now we implement basic version.

    # 3.1 Delete old chunks from vector store
    await delete_document_by_metadata(document_id)

    # 3.2 Add new chunks
    documents = []

    for i, chunk in enumerate(chunks):
        metadata = {
            "document_id": str(document_id),
            "filename": filename,
            "chunk_index": i,
            "created_at": doc.created_at,  # Keep original
            "is_active": doc.is_active,
            "file_type": file_type,
            "file_size_bytes": len(content.encode("utf-8")),
        }
        if url:
            metadata["url"] = url
        documents.append(Document(page_content=chunk, metadata=metadata))

    # Add to Vector Store
    await add_documents(documents)

    # 3.3 Update DB record content
    # We need a db function for this.
    # Assuming update_faq_document_content exists or we add it.
    from app.infrastructure.db import update_faq_document_content

    await update_faq_document_content(
        document_id, content, len(content.encode("utf-8"))
    )

    return True


MAX_URL_CONTENT_SIZE = settings.FAQ_MAX_URL_CONTENT_SIZE

# Blocked hostnames for SSRF protection
_BLOCKED_HOSTNAMES = frozenset(
    [
        "localhost",
        "127.0.0.1",
        "0.0.0.0",
        "metadata",
        "metadata.google.internal",
        "169.254.169.254",
    ]
)


def _validate_url_security(url: str) -> None:
    """Validate URL to prevent SSRF attacks.

    Args:
        url: URL to validate

    Raises:
        ValueError: If URL targets internal/private resources
    """
    parsed = urlparse(url)
    hostname = parsed.hostname

    if not hostname:
        raise ValueError("유효하지 않은 URL입니다")

    hostname_lower = hostname.lower()

    # Block known internal hostnames
    if hostname_lower in _BLOCKED_HOSTNAMES:
        raise ValueError("내부 URL은 허용되지 않습니다")

    # Check for private/internal IP addresses
    try:
        # Resolve hostname to IP
        ip_str = socket.gethostbyname(hostname)
        ip = ipaddress.ip_address(ip_str)

        if ip.is_private or ip.is_loopback or ip.is_reserved or ip.is_link_local:
            raise ValueError("내부 네트워크 URL은 허용되지 않습니다")
    except socket.gaierror:
        # Cannot resolve hostname - let httpx handle it
        pass
    except ValueError:
        # Not a valid IP - continue with hostname check
        pass


async def _fetch_url_content(url: str) -> str:
    """Fetch and extract text content from a URL.

    Args:
        url: URL to fetch

    Returns:
        Extracted text content

    Raises:
        ValueError: If URL cannot be fetched or parsed
    """
    # Validate URL security (SSRF protection)
    _validate_url_security(url)

    logger.debug(f"Fetching URL: {url}")

    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()

            # Check content size
            content_length = response.headers.get("content-length")
            if content_length and int(content_length) > MAX_URL_CONTENT_SIZE:
                raise ValueError(
                    f"콘텐츠 크기가 너무 큽니다: {int(content_length) // (1024 * 1024)}MB"
                )
    except httpx.HTTPStatusError as e:
        raise ValueError(f"URL 요청 실패: HTTP {e.response.status_code}") from e
    except httpx.RequestError as e:
        raise ValueError(f"URL 요청 오류: {e}") from e

    # Additional size check for actual content
    if len(response.content) > MAX_URL_CONTENT_SIZE:
        raise ValueError("콘텐츠 크기가 10MB를 초과합니다")

    content_type = response.headers.get("content-type", "")
    if "text/html" not in content_type and "text/plain" not in content_type:
        raise ValueError(f"지원하지 않는 콘텐츠 타입: {content_type}")

    soup = BeautifulSoup(response.text, "lxml")

    for element in soup(["script", "style", "nav", "footer", "header"]):
        element.decompose()

    text = soup.get_text(separator="\n", strip=True)

    if not text.strip():
        raise ValueError("URL에서 텍스트를 추출할 수 없습니다")

    logger.debug(f"Extracted {len(text)} characters from URL")
    return text


async def upload_faq_from_url(
    url: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> FAQUploadResponse:
    """Upload FAQ content from a URL.

    Args:
        url: URL to fetch FAQ content from
        chunk_size: Target chunk size in characters
        chunk_overlap: Overlap between chunks

    Returns:
        FAQUploadResponse with document info and stats

    Raises:
        ValueError: If URL cannot be fetched or processing fails
    """
    logger.info(f"Uploading FAQ from URL: {url}")

    text = await _fetch_url_content(url)

    chunks = _chunk_text(text, chunk_size, chunk_overlap)

    if not chunks:
        raise ValueError("URL에서 유효한 텍스트를 추출할 수 없습니다")

    parsed_url = urlparse(url)
    filename = parsed_url.netloc + parsed_url.path

    return await _store_faq_chunks(
        chunks=chunks,
        filename=filename,
        file_type="url",
        file_size_bytes=len(text.encode("utf-8")),
        full_text=text,
        url=url,
        message="URL에서 FAQ 문서가 성공적으로 업로드되었습니다.",
    )


async def upload_faq_text(
    title: str,
    content: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> FAQUploadResponse:
    """Upload FAQ content from direct text input.

    Args:
        title: Document title (used as filename)
        content: Text content
        chunk_size: Target chunk size
        chunk_overlap: Overlap between chunks

    Returns:
        FAQUploadResponse with document info
    """
    logger.info(f"Uploading FAQ from text input: {title}")

    chunks = _chunk_text(content, chunk_size, chunk_overlap)

    if not chunks:
        raise ValueError("입력된 텍스트에서 유효한 내용을 추출할 수 없습니다")

    # Ensure title ends with .txt for consistency if not present
    filename = f"{title}.txt" if not title.lower().endswith(".txt") else title

    return await _store_faq_chunks(
        chunks=chunks,
        filename=filename,
        file_type="txt",  # Treat as txt file
        file_size_bytes=len(content.encode("utf-8")),
        full_text=content,
        message="텍스트로 FAQ 문서가 성공적으로 등록되었습니다.",
    )
