"""LLM-based conversation parser using LangChain structured output."""

from functools import lru_cache

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from loguru import logger

from app.domain import Conversation, ParsedConversation, Turn

# Maximum input text length (~25K tokens)
MAX_INPUT_LENGTH = 100_000

PARSER_SYSTEM_PROMPT = """당신은 상담 대화 분석 전문가입니다.

주어진 텍스트에서 상담원(agent)과 고객(customer) 간의 대화를 추출해주세요.

규칙:
1. 각 메시지의 화자를 정확히 구분하세요 (agent 또는 customer)
2. 상담원/상담사/CS담당자/Agent = "agent"
3. 고객/손님/구매자/Customer = "customer"
4. 대화 순서를 유지하세요
5. 메시지 내용은 원문 그대로 유지하세요
6. 인사말, 문의 내용, 답변 등 모든 발화를 포함하세요

텍스트가 명시적인 대화 형식이 아니더라도 대화 내용을 추출해주세요."""

PARSER_HUMAN_PROMPT = """다음 텍스트에서 대화를 추출해주세요:

{text}"""


@lru_cache(maxsize=1)
def _get_parser_chain():
    """Create and cache the LLM parser chain with structured output.

    Returns:
        A LangChain chain configured for conversation parsing.
    """
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0,
        timeout=30,
        max_retries=2,
    )

    structured_llm = llm.with_structured_output(ParsedConversation)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", PARSER_SYSTEM_PROMPT),
            ("human", PARSER_HUMAN_PROMPT),
        ]
    )

    return prompt | structured_llm


def _convert_to_conversation(parsed: ParsedConversation) -> Conversation:
    """Convert ParsedConversation to domain Conversation model.

    Args:
        parsed: The parsed conversation from LLM output.

    Returns:
        A Conversation domain object.
    """
    turns = [Turn(speaker=msg.role, message=msg.content) for msg in parsed.messages]
    return Conversation(
        turns=turns,
        metadata={"parsing_method": "llm"},
    )


async def parse_conversation_with_llm(raw_content: str) -> Conversation:
    """Parse raw text into a Conversation using LLM.

    Uses GPT-4o-mini with structured output to parse any format
    of conversation text into a structured Conversation object.

    Args:
        raw_content: Raw text content containing conversation data.

    Returns:
        A Conversation object with parsed turns.

    Raises:
        ValueError: If the input is empty, whitespace-only, or too long.
    """
    if not raw_content or not raw_content.strip():
        raise ValueError("입력 텍스트가 비어있습니다")

    if len(raw_content) > MAX_INPUT_LENGTH:
        raise ValueError(
            f"입력 텍스트가 너무 깁니다. 최대 {MAX_INPUT_LENGTH:,}자까지 지원됩니다."
        )

    logger.info("Parsing conversation with LLM")

    chain = _get_parser_chain()
    parsed = await chain.ainvoke({"text": raw_content})

    logger.debug(f"LLM parsed {len(parsed.messages)} messages")

    return _convert_to_conversation(parsed)
