"""Domain models for FAQ RAG functionality.

This module contains entities and value objects for FAQ document
management and vector search operations.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class FAQDocument(BaseModel):
    """A FAQ document uploaded to the system.

    Represents a PDF, TXT file, or URL containing FAQ content
    that has been processed and stored.
    """

    id: UUID
    url: str | None = None
    filename: str | None = None
    file_type: str | None = None
    file_size_bytes: int | None = None
    created_at: datetime | None = None


class FAQChunk(BaseModel):
    """A chunk of FAQ document content with its embedding.

    Represents a segment of text from a FAQ document that has been
    vectorized for similarity search.
    """

    id: UUID
    document_id: UUID | None = None
    collection_id: UUID | None = None
    content: str
    embedding: list[float] = Field(min_length=1536, max_length=1536)
    is_active: bool = True
    cmetadata: dict | None = None
    created_at: datetime | None = (
        None  # Not directly in FAQEmbedding but often useful if derived
    )


class FAQSearchResult(BaseModel):
    """A single result from FAQ similarity search.

    Contains the matched chunk content and its relevance score.
    """

    chunk_id: UUID | None = None
    document_id: UUID | None = None
    content: str
    similarity_score: float = Field(ge=0.0, le=1.0)
    filename: str | None = None
    token_count: int | None = None


class FAQContext(BaseModel):
    """Collection of FAQ search results for analysis context.

    Provides methods to format results for LLM prompts.
    """

    results: list[FAQSearchResult] = Field(default_factory=list)

    @property
    def has_results(self) -> bool:
        """Check if any FAQ results were found."""
        return len(self.results) > 0

    def to_prompt_context(self) -> str:
        """Format FAQ results as context string for LLM prompts.

        Returns:
            Formatted string with FAQ content, or empty string if no results.
        """
        if not self.results:
            return ""

        lines = ["## 참고 FAQ 정보", ""]

        for i, result in enumerate(self.results, 1):
            lines.append(f"### FAQ #{i} (출처: {result.filename})")
            lines.append(result.content)
            lines.append("")

        return "\n".join(lines)


class FAQListItem(BaseModel):
    """Summary of a FAQ document for list display.

    Contains essential information for UI listing.
    """

    id: UUID
    url: str | None = None
    filename: str | None = None
    file_type: str | None = None
    file_size_bytes: int | None = None
    content_preview: str | None = None
    created_at: datetime | None = None
    is_active: bool = True


class FAQUploadResponse(BaseModel):
    """Response after successful FAQ document upload.

    Contains the created document info and processing stats.
    """

    document: FAQListItem
    chunks_created: int
    message: str = "FAQ 문서가 성공적으로 업로드되었습니다."
