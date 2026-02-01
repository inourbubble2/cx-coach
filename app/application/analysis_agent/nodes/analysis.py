import uuid
from datetime import UTC, datetime
from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from loguru import logger
from pydantic import BaseModel, Field

from app.core.config import settings
from app.domain import (
    AnalysisResult,
    Conversation,
    FAQAccuracy,
    Improvement,
    ScoresWithEvidence,
)
from app.domain.agent import GraphState
from app.infrastructure.llm.prompts import (
    ANALYSIS_HUMAN_PROMPT,
    ANALYSIS_HUMAN_PROMPT_WITH_FAQ,
    ANALYSIS_SYSTEM_PROMPT,
    ANALYSIS_SYSTEM_PROMPT_WITH_FAQ,
)


class LLMFAQAccuracy(BaseModel):
    """LLM 응답용 FAQ 정확성 모델."""

    correct_info: list[str] = Field(
        default_factory=list, description="FAQ와 일치하는 정확한 정보"
    )
    incorrect_info: list[str] = Field(
        default_factory=list, description="FAQ와 다른 잘못된 정보"
    )
    missing_info: list[str] = Field(
        default_factory=list, description="누락된 중요 정보"
    )


class LLMAnalysisResponse(BaseModel):
    """LLM 응답용 모델 (structured output)."""

    scores_with_evidence: ScoresWithEvidence = Field(
        description="근거가 포함된 항목별 점수"
    )
    total_score: int = Field(ge=0, le=100, description="종합 점수 (100점 만점)")
    strengths: list[str] = Field(description="잘한 점 목록")
    improvements: list[Improvement] = Field(description="개선 사항 목록")
    overall_feedback: str = Field(description="종합적인 코칭 코멘트")
    faq_accuracy: LLMFAQAccuracy | None = Field(
        default=None, description="FAQ 정확성 평가 (FAQ 사용 시)"
    )


def _format_conversation(conversation: Conversation) -> str:
    """Format conversation for LLM prompt."""
    lines = []
    for turn in conversation.turns:
        speaker_label = "상담원" if turn.speaker == "agent" else "고객"
        lines.append(f"{speaker_label}: {turn.message}")
    return "\n".join(lines)


def _to_analysis_result(
    response: LLMAnalysisResponse,
    request_id: str,
    has_faq_context: bool = False,
) -> AnalysisResult:
    """Convert LLM structured response to AnalysisResult."""
    # Convert scores_with_evidence to simple scores for backward compatibility
    scores = response.scores_with_evidence.to_scores()

    # Convert FAQ accuracy if present
    faq_accuracy = None
    if response.faq_accuracy or has_faq_context:
        faq_accuracy = FAQAccuracy(
            has_faq_context=has_faq_context,
            correct_info=response.faq_accuracy.correct_info
            if response.faq_accuracy
            else [],
            incorrect_info=response.faq_accuracy.incorrect_info
            if response.faq_accuracy
            else [],
            missing_info=response.faq_accuracy.missing_info
            if response.faq_accuracy
            else [],
        )

    # Calculate total score deterministically (Sum of 6 scores * 1.66... approx or let LLM decide)
    # Actually, simplistic approach: (Sum / 60) * 100
    total_raw = (
        scores.clarification
        + scores.empathy_tone
        + scores.solution_accuracy
        + scores.actionability
        + scores.confirmation_closure
        + scores.compliance_safety
    )

    calculated_total_score = int((total_raw / 60) * 100)

    return AnalysisResult(
        request_id=request_id,
        analyzed_at=datetime.now(UTC),
        scores=scores,
        scores_with_evidence=response.scores_with_evidence,
        total_score=calculated_total_score,
        strengths=response.strengths,
        improvements=response.improvements,
        overall_feedback=response.overall_feedback,
        faq_accuracy=faq_accuracy,
    )


async def analysis_node(state: GraphState) -> dict[str, Any]:
    """Generate analysis result using LLM."""
    logger.debug("Executing Analysis Node")

    conversation = state["conversation"]
    faq_context = state.get("faq_context")

    formatted_conversation = _format_conversation(conversation)
    request_id = str(uuid.uuid4())

    llm = ChatOpenAI(
        model=settings.OPENAI_CHAT_MODEL,
        temperature=0.3,
        api_key=settings.OPENAI_API_KEY,
    )
    structured_llm = llm.with_structured_output(LLMAnalysisResponse)

    if faq_context and faq_context.has_results:
        logger.debug("Using FAQ context for analysis")
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", ANALYSIS_SYSTEM_PROMPT_WITH_FAQ),
                ("human", ANALYSIS_HUMAN_PROMPT_WITH_FAQ),
            ]
        )
        chain = prompt | structured_llm
        response: LLMAnalysisResponse = await chain.ainvoke(
            {
                "conversation": formatted_conversation,
                "faq_context": faq_context.to_prompt_context(),
            }
        )
    else:
        logger.debug("Using standard analysis without FAQ")
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", ANALYSIS_SYSTEM_PROMPT),
                ("human", ANALYSIS_HUMAN_PROMPT),
            ]
        )
        chain = prompt | structured_llm
        response: LLMAnalysisResponse = await chain.ainvoke(
            {"conversation": formatted_conversation}
        )

    has_faq = faq_context is not None and faq_context.has_results
    result = _to_analysis_result(response, request_id, has_faq_context=has_faq)
    return {"analysis_result": result}
