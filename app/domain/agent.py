from typing import TypedDict

from app.domain import AnalysisResult, Conversation, FAQContext


class GraphState(TypedDict):
    """LangGraph state definition for the analysis agent."""

    conversation: Conversation
    skip_retrieval: bool
    faq_context: FAQContext | None
    analysis_result: AnalysisResult | None
