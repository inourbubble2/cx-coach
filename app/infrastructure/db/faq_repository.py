from datetime import datetime
from uuid import UUID

from sqlalchemy import delete, select, update

from app.domain import FAQListItem
from app.infrastructure.db.database import get_session
from app.infrastructure.db.models.faq import FAQDocument


async def create_document(
    filename: str | None,
    file_type: str | None,
    file_size_bytes: int | None,
    url: str | None = None,
    content: str | None = None,
) -> FAQListItem:
    """Create a new FAQ document record.

    Args:
        filename: Filename (optional if URL)
        file_type: File extension/type
        file_size_bytes: Size in bytes
        url: Source URL (optional)
        content: Full text content (optional)

    Returns:
        Created FAQ list item
    """
    async for session in get_session():
        db_doc = FAQDocument(
            filename=filename,
            file_type=file_type,
            file_size_bytes=file_size_bytes,
            url=url,
            content=content,
            created_at=datetime.now(),
            is_active=True,
        )
        session.add(db_doc)
        await session.commit()
        await session.refresh(db_doc)

        content_preview = None
        if db_doc.content:
            content_preview = db_doc.content[:300] + (
                "..." if len(db_doc.content) > 300 else ""
            )

        return FAQListItem(
            id=db_doc.id,
            filename=db_doc.filename,
            file_type=db_doc.file_type,
            file_size_bytes=db_doc.file_size_bytes,
            url=db_doc.url,
            content_preview=content_preview,
            created_at=db_doc.created_at,
            is_active=db_doc.is_active,
        )


async def list_documents(
    limit: int = 100,
    include_inactive: bool = False,
) -> list[FAQListItem]:
    """List FAQ documents.

    Args:
        limit: Max results
        include_inactive: Include inactive documents

    Returns:
        List of FAQ list items
    """
    query = select(FAQDocument).order_by(FAQDocument.created_at.desc()).limit(limit)

    if not include_inactive:
        # If we have is_active, filter. Currently models/faq.py has it.
        try:
            query = query.where(FAQDocument.is_active == True)
        except AttributeError:
             # Fallback if migration not applied (runtime safety)
             pass

    items = []
    async for session in get_session():
        result = await session.execute(query)
        docs = result.scalars().all()

        for doc in docs:
            content_preview = None
            if doc.content:
                content_preview = doc.content[:300] + (
                    "..." if len(doc.content) > 300 else ""
                )

            items.append(
                FAQListItem(
                    id=doc.id,
                    filename=doc.filename,
                    file_type=doc.file_type,
                    file_size_bytes=doc.file_size_bytes,
                    url=doc.url,
                    content_preview=content_preview,
                    created_at=doc.created_at,
                    is_active=doc.is_active,
                )
            )
    return items


async def update_document_active_status(document_id: UUID, is_active: bool) -> bool:
    """Update FAQ document active status.

    Args:
        document_id: ID to update
        is_active: New status

    Returns:
        True if found and updated
    """
    async for session in get_session():
        query = (
            update(FAQDocument)
            .where(FAQDocument.id == document_id)
            .values(is_active=is_active)
        )
        result = await session.execute(query)
        await session.commit()
        return result.rowcount > 0
    return False


async def delete_document(document_id: UUID) -> bool:
    """Delete a FAQ document record.

    Note: This does NOT delete associated embeddings if cascading is not set up in DB.
    Service layer should handle embedding deletion.

    Args:
        document_id: ID to delete

    Returns:
        True if found and deleted
    """
    async for session in get_session():
        query = delete(FAQDocument).where(FAQDocument.id == document_id)
        result = await session.execute(query)
        await session.commit()
        return result.rowcount > 0
    return False


async def update_document_content(
    document_id: UUID,
    content: str,
    file_size_bytes: int,
) -> bool:
    """Update FAQ document content.

    Args:
        document_id: ID to update
        content: New content
        file_size_bytes: New size

    Returns:
        True if found and updated
    """
    async for session in get_session():
        query = select(FAQDocument).where(FAQDocument.id == document_id)
        result = await session.execute(query)
        doc = result.scalar_one_or_none()

        if doc:
            doc.content = content
            doc.file_size_bytes = file_size_bytes
            await session.commit()
            return True
        return False
