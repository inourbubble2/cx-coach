"""Analysis service orchestrating conversation analysis workflow.

This service providing the main entry point for analyzing counseling conversations.
"""

from loguru import logger

from app.application.analysis_agent.graph import analysis_graph
from app.application.analysis_agent.nodes.guardrail import ConversationGuardrailError
from app.domain import AnalysisResult, Conversation
from app.infrastructure.db import save_analysis, save_conversation

# Re-export for convenience
__all__ = ["analyze_conversation", "ConversationGuardrailError"]


async def _save_conversation_to_db(conversation: Conversation) -> Conversation:
    """Save conversation to database, returning saved instance with ID."""
    try:
        return await save_conversation(conversation)
    except Exception as e:
        logger.warning(f"Failed to save conversation to DB: {e}")
        return conversation


async def _save_result_to_db(result: AnalysisResult) -> None:
    """Save analysis result to database, logging errors without raising."""
    try:
        await save_analysis(result)
    except Exception as e:
        logger.warning(f"Failed to save analysis result to DB: {e}")


async def analyze_conversation(
    conversation: Conversation, use_faq: bool = True
) -> AnalysisResult:
    """Analyze a conversation object.

    Args:
        conversation: The conversation to analyze
        use_faq: Whether to search and include FAQ context

    Returns:
        AnalysisResult with scores and feedback
    """
    logger.info(f"Analyzing {conversation.turn_count} turns (use_faq={use_faq})")

    # Save conversation first to get ID
    saved_conversation = await _save_conversation_to_db(conversation)

    initial_state = {
        "conversation": saved_conversation,
        "skip_retrieval": not use_faq,
        "faq_context": None,
        "analysis_result": None,
    }

    result_state = await analysis_graph.ainvoke(initial_state)
    result = result_state["analysis_result"]

    # Link conversation_id to result
    if saved_conversation.id:
        result = result.model_copy(update={"conversation_id": saved_conversation.id})

    await _save_result_to_db(result)
    return result
