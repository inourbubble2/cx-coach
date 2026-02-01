"""FAQ Query Repository for direct vector store access.

Implements list and delete operations using direct SQL on the
vector embeddings table, supporting the Single Table Architecture.
"""

from datetime import datetime
from uuid import UUID

from loguru import logger
from sqlalchemy import text

from app.domain import FAQListItem
from app.infrastructure.db.database import get_session


async def list_documents(
    include_inactive: bool = False,
    limit: int = 100,
) -> list[FAQListItem]:
    """List FAQ documents by aggregating metadata from vector table.

    Args:
        include_inactive: Include inactive documents (not used in query yet)
        limit: Maximum number of results

    Returns:
        List of FAQ documents
    """
    logger.debug("Listing FAQ documents from vector store")

    # We group by document_id found in metadata to reconstruct document list
    query = text("""
        SELECT
            document_id as id,
            MAX(filename) as filename,
            MAX(file_type) as file_type,
            MAX(file_size_bytes) as file_size_bytes,
            MAX(created_at) as created_at,
            MAX(is_active::int)::boolean as is_active
        FROM faq_embeddings
        GROUP BY document_id
        ORDER BY created_at DESC
        LIMIT :limit
    """)

    items = []
    async for session in get_session():
        result = await session.execute(query, {"limit": limit})
        rows = result.fetchall()

        for row in rows:
            try:
                # Handle potential missing data gracefully
                if not row.id:
                    continue

                created_at = row.created_at
                # If driver returns string, parse it. If datetime, use as is.
                if isinstance(created_at, str):
                    created_at = datetime.fromisoformat(
                        created_at.replace("Z", "+00:00")
                    )

                items.append(
                    FAQListItem(
                        id=UUID(row.id),
                        filename=row.filename or "Unknown",
                        file_type=row.file_type or "txt",
                        file_size_bytes=row.file_size_bytes or 0,
                        created_at=created_at,
                        is_active=row.is_active if row.is_active is not None else True,
                    )
                )
            except Exception as e:
                logger.warning(f"Error parsing FAQ document row: {e}")
                continue

    # Filter inactive if needed (though we could do it in SQL)
    if not include_inactive:
        items = [item for item in items if item.is_active]

    return items


async def delete_document_by_metadata(document_id: UUID) -> bool:
    """Delete all chunks for a document by document_id metadata.

    Args:
        document_id: Document UUID

    Returns:
        True if deleted
    """
    logger.debug(f"Deleting FAQ document chunks: {document_id}")

    query = text("""
        DELETE FROM faq_embeddings
        WHERE document_id = :document_id
    """)

    async for session in get_session():
        result = await session.execute(query, {"document_id": str(document_id)})
        await session.commit()

        # rowcount might not be reliable in some asyncpg versions/drivers but usually works
        deleted_count = result.rowcount
        logger.info(f"Deleted {deleted_count} chunks for document {document_id}")
        return deleted_count > 0

    return False


async def update_document_active_status(document_id: UUID, is_active: bool) -> bool:
    """Update is_active status for all chunks of a document.

    Args:
        document_id: Document UUID
        is_active: New active status

    Returns:
        True if updated successfully
    """
    logger.debug(f"Updating FAQ document {document_id} active status to {is_active}")

    query = text("""
        UPDATE faq_embeddings
        SET is_active = :is_active
        WHERE document_id = :document_id
    """)

    async for session in get_session():
        result = await session.execute(
            query, {"document_id": str(document_id), "is_active": is_active}
        )
        await session.commit()

        updated_count = result.rowcount
        logger.info(f"Updated {updated_count} chunks for document {document_id}")
        return updated_count > 0

    return False
