"""Unit tests for FAQ service."""

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from langchain_core.documents import Document

from app.application.faq_service import search_faq, upload_faq_document
from app.domain import FAQListItem


@pytest.fixture
def mock_vector_store():
    with patch(
        "app.application.faq_service.add_documents", new_callable=AsyncMock
    ) as mock_add:
        mock_add.return_value = ["id1", "id2"]
        yield mock_add


@pytest.fixture
def mock_similarity_search():
    with patch(
        "app.application.faq_service.similarity_search", new_callable=AsyncMock
    ) as mock_search:
        # Return list of (Document, score) tuples
        mock_search.return_value = [
            (
                Document(
                    page_content="chunk1",
                    metadata={"document_id": str(uuid4()), "filename": "test.txt"},
                ),
                0.9,
            ),
            (
                Document(
                    page_content="chunk2",
                    metadata={"document_id": str(uuid4()), "filename": "test.txt"},
                ),
                0.5,
            ),
        ]
        yield mock_search


@pytest.fixture
def mock_db_ops():
    with (
        patch(
            "app.application.faq_service.create_faq_document", new_callable=AsyncMock
        ) as mock_create,
        patch(
            "app.application.faq_service.delete_faq_document", new_callable=AsyncMock
        ) as mock_delete,
        patch(
            "app.infrastructure.db.faq_query_repository.delete_document_by_metadata",
            new_callable=AsyncMock,
        ) as mock_delete_meta,
    ):
        # Setup mock document
        mock_doc = MagicMock(spec=FAQListItem)
        mock_doc.id = uuid4()
        mock_doc.created_at = datetime.now()
        mock_create.return_value = mock_doc

        mock_delete.return_value = True
        mock_delete_meta.return_value = True

        yield {
            "create": mock_create,
            "delete": mock_delete,
            "delete_meta": mock_delete_meta,
        }


@pytest.mark.asyncio
async def test_upload_faq_document(mock_vector_store, mock_db_ops):
    """Test uploading document integrates with vector store."""
    content = b"test content"
    filename = "test.txt"

    # Mock text extraction/chunking inside the service is hard without refactoring imports or more patching
    # So we'll patch the private methods for simplicity
    with (
        patch(
            "app.application.faq_service._extract_text_from_txt",
            return_value="chunk1 chunk2",
        ),
        patch(
            "app.application.faq_service._chunk_text", return_value=["chunk1", "chunk2"]
        ),
    ):
        response = await upload_faq_document(content, filename)

        # Verify DB creation was called
        mock_db_ops["create"].assert_called_once()
        call_kwargs = mock_db_ops["create"].call_args[1]
        assert call_kwargs["filename"] == "test.txt"
        assert call_kwargs["file_type"] == "txt"

        # Verify vector store was called
        mock_vector_store.assert_called_once()
        args = mock_vector_store.call_args[0][0]
        assert len(args) == 2

        # Verify metadata uses ID from DB record (mock_doc.id)
        # Note: We can't easily check the exact ID unless we capture the mock_doc

        # Verify response matches
        assert response.chunks_created == 2


@pytest.mark.asyncio
async def test_search_faq(mock_similarity_search, mock_db_ops):
    """Test searching FAQ integrates with vector store."""
    query = "test query"

    context = await search_faq(query, limit=2, threshold=0.8)

    # Verify vector store search called
    mock_similarity_search.assert_called_once_with(query, k=2)

    # Verify filtering
    # We returned scores 0.9 and 0.5. Threshold is 0.8. Should check result count.
    # Wait, the search_faq implementation iterates and filters.
    assert len(context.results) == 1
    assert context.results[0].similarity_score == 0.9
