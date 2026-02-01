"""Guardrail node for filtering irrelevant content."""

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from loguru import logger
from pydantic import BaseModel, Field

from app.domain.agent import GraphState


class GuardrailResult(BaseModel):
    """Result of guardrail check."""

    is_valid_consultation: bool = Field(
        description="True if the content is a valid customer service consultation"
    )
    reason: str = Field(description="Reason for the decision")


GUARDRAIL_SYSTEM_PROMPT = """당신은 고객 상담 대화 분류 전문가입니다.
주어진 텍스트가 고객 상담/서비스 대화인지 판단하세요.

## 유효한 상담 대화 (is_valid_consultation = true)
- 고객과 상담원 간의 대화
- 제품/서비스 문의, 불만 접수, 주문 확인, 기술 지원 등
- 콜센터, 채팅 상담, 이메일 상담 등 모든 형태의 고객 서비스

## 무효한 콘텐츠 (is_valid_consultation = false)
- 일반 대화, 친구간 대화
- 소설, 시, 뉴스 기사 등 창작물
- 코드, 기술 문서
- 의미없는 텍스트, 스팸
- 상담과 무관한 업무 대화
- 욕설, 비속어만 있는 텍스트

간결하게 판단하고, 이유를 한 문장으로 설명하세요."""

GUARDRAIL_HUMAN_PROMPT = """다음 텍스트가 고객 상담 대화인지 판단하세요:

{conversation}"""


class ConversationGuardrailError(Exception):
    """Raised when conversation fails guardrail check."""

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"상담 분석 불가: {reason}")


async def guardrail_node(state: GraphState) -> GraphState:
    """Check if the conversation is a valid customer service consultation.

    Raises:
        ConversationGuardrailError: If content is not a valid consultation
    """
    conversation = state["conversation"]
    logger.info(
        f"Guardrail check for conversation with {conversation.turn_count} turns"
    )

    # Format conversation for the prompt
    conv_text = "\n".join(
        f"{'상담원' if t.speaker == 'agent' else '고객'}: {t.message}"
        for t in conversation.turns
    )

    # Use a fast, cheap model for guardrail
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    structured_llm = llm.with_structured_output(GuardrailResult)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", GUARDRAIL_SYSTEM_PROMPT),
            ("human", GUARDRAIL_HUMAN_PROMPT),
        ]
    )

    chain = prompt | structured_llm

    try:
        result: GuardrailResult = await chain.ainvoke({"conversation": conv_text})

        if not result.is_valid_consultation:
            logger.warning(f"Guardrail rejected: {result.reason}")
            raise ConversationGuardrailError(result.reason)

        logger.info(f"Guardrail passed: {result.reason}")
        return state

    except ConversationGuardrailError:
        raise
    except Exception as e:
        logger.error(f"Guardrail check failed with error: {e}")
        # On LLM error, allow through (fail-open for availability)
        logger.warning("Guardrail failed-open due to error")
        return state
