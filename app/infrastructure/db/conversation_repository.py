"""Database repository for conversations using SQLAlchemy."""

import uuid
from datetime import UTC, datetime

from loguru import logger
from sqlalchemy import select

from app.domain import Conversation, Turn
from app.infrastructure.db.database import get_session
from app.infrastructure.db.models.conversation import Conversation as DBConversation


def _db_to_domain(db_row: DBConversation) -> Conversation:
    """Convert DB model to Domain model."""
    turns = [Turn(**turn) for turn in db_row.turns]
    return Conversation(
        id=db_row.id,
        created_at=db_row.created_at,
        turns=turns,
        metadata=db_row.metadata_,
    )


def _domain_to_db(conversation: Conversation) -> DBConversation:
    """Convert Domain model to DB model."""
    return DBConversation(
        id=conversation.id or uuid.uuid4(),
        created_at=conversation.created_at or datetime.now(UTC),
        turn_count=conversation.turn_count,
        turns=[turn.model_dump(mode="json") for turn in conversation.turns],
        metadata_=conversation.metadata or {},
    )


async def save_conversation(conversation: Conversation) -> Conversation:
    """Save a conversation to the database.

    If the conversation has no id, one will be generated.
    Returns the saved conversation with id and created_at populated.
    """
    db_obj = _domain_to_db(conversation)
    logger.debug(f"Saving conversation: {db_obj.id}")

    async for session in get_session():
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        saved = _db_to_domain(db_obj)
        logger.info(f"Conversation saved: {saved.id}")
        return saved

    raise RuntimeError("Failed to obtain database session")


async def get_conversation(conversation_id: uuid.UUID) -> Conversation | None:
    """Retrieve a conversation by ID."""
    logger.debug(f"Fetching conversation: {conversation_id}")

    query = select(DBConversation).where(DBConversation.id == conversation_id)

    async for session in get_session():
        result = await session.execute(query)
        db_obj = result.scalar_one_or_none()
        if db_obj:
            return _db_to_domain(db_obj)
        return None

    return None
