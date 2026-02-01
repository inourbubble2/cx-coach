from typing import Any

from loguru import logger

from app.application.faq_service import search_faq
from app.domain.agent import GraphState


async def retrieval_node(state: GraphState) -> dict[str, Any]:
    """Search for relevant FAQs based on conversation content.

    Extracts recent customer messages from the conversation to build
    a query for FAQ similarity search.

    Returns:
        Dict with faq_context if search performed, empty dict otherwise.
    """
    logger.debug("Executing Retrieval Node")

    if state.get("skip_retrieval"):
        logger.debug("Retrieval skipped by request")
        return {}

    conversation = state.get("conversation")
    if not conversation or not conversation.turns:
        logger.debug("No conversation turns, skipping retrieval")
        return {}

    customer_messages = [
        turn.message for turn in conversation.turns if turn.speaker == "customer"
    ]

    if not customer_messages:
        logger.debug("No customer messages found, skipping retrieval")
        return {}

    recent_messages = customer_messages[]
    query = " ".join(recent_messages)

    logger.info(f"Searching FAQ with query: {query}...")

    try:
        faq_context = await search_faq(query, limit=5, threshold=0.6)
        logger.info(f"FAQ retrieval found {len(faq_context.results)} results")
        return {"faq_context": faq_context}
    except Exception as e:
        logger.warning(f"FAQ retrieval failed: {e}")
        return {}
