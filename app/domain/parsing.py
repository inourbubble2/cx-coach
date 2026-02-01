"""Domain models for conversation parsing."""

from typing import Literal

from pydantic import BaseModel, Field


class ParsedMessage(BaseModel):
    """A single parsed message from a conversation.

    Attributes:
        role: The speaker role - either "agent" (customer service rep)
              or "customer" (the person seeking help).
        content: The actual message content.
    """

    role: Literal["agent", "customer"] = Field(
        description="화자 역할: 'agent'(상담원) 또는 'customer'(고객)"
    )
    content: str = Field(description="메시지 내용")


class ParsedConversation(BaseModel):
    """A parsed conversation containing multiple messages.

    This is the output schema used by LLM structured output
    to parse raw conversation text into a structured format.
    """

    messages: list[ParsedMessage] = Field(
        description="대화 메시지 목록 (시간 순서대로 정렬)",
        min_length=1,
    )
