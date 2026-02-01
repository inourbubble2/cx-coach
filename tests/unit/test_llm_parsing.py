"""Unit tests for LLM conversation parser."""

from unittest.mock import AsyncMock, patch

import pytest

from app.domain import Conversation, ParsedConversation, ParsedMessage


class TestParsedModels:
    """Tests for ParsedMessage and ParsedConversation models."""

    def test_parsed_message_agent(self):
        """Test ParsedMessage with agent role."""
        msg = ParsedMessage(role="agent", content="안녕하세요")
        assert msg.role == "agent"
        assert msg.content == "안녕하세요"

    def test_parsed_message_customer(self):
        """Test ParsedMessage with customer role."""
        msg = ParsedMessage(role="customer", content="문의드립니다")
        assert msg.role == "customer"
        assert msg.content == "문의드립니다"

    def test_parsed_message_invalid_role(self):
        """Test ParsedMessage rejects invalid role."""
        with pytest.raises(ValueError):
            ParsedMessage(role="bot", content="hello")

    def test_parsed_conversation(self):
        """Test ParsedConversation with messages."""
        conv = ParsedConversation(
            messages=[
                ParsedMessage(role="agent", content="안녕하세요"),
                ParsedMessage(role="customer", content="네"),
            ]
        )
        assert len(conv.messages) == 2

    def test_parsed_conversation_empty_messages_raises_error(self):
        """Test ParsedConversation rejects empty messages list."""
        with pytest.raises(ValueError):
            ParsedConversation(messages=[])


class TestParseConversationWithLLM:
    """Tests for parse_conversation_with_llm function."""

    @pytest.fixture
    def mock_llm_response(self):
        """Create a mock LLM response."""
        return ParsedConversation(
            messages=[
                ParsedMessage(role="agent", content="안녕하세요, 무엇을 도와드릴까요?"),
                ParsedMessage(role="customer", content="결제 오류가 발생했어요"),
                ParsedMessage(role="agent", content="확인해보겠습니다"),
            ]
        )

    @pytest.mark.asyncio
    async def test_parse_simple_conversation(self, mock_llm_response):
        """Test parsing a simple conversation."""
        from app.infrastructure.llm.conversation_parser import (
            parse_conversation_with_llm,
        )

        raw_text = """
        상담원이 "안녕하세요, 무엇을 도와드릴까요?"라고 인사했습니다.
        고객이 "결제 오류가 발생했어요"라고 말했습니다.
        상담원이 "확인해보겠습니다"라고 답했습니다.
        """

        with patch(
            "app.infrastructure.llm.conversation_parser._get_parser_chain"
        ) as mock_chain:
            mock_chain.return_value.ainvoke = AsyncMock(return_value=mock_llm_response)

            result = await parse_conversation_with_llm(raw_text)

            assert isinstance(result, Conversation)
            assert result.turn_count == 3
            assert result.turns[0].speaker == "agent"
            assert result.turns[0].message == "안녕하세요, 무엇을 도와드릴까요?"
            assert result.turns[1].speaker == "customer"
            assert result.turns[2].speaker == "agent"

    @pytest.mark.asyncio
    async def test_parse_freeform_text(self, mock_llm_response):
        """Test parsing freeform/unstructured text."""
        from app.infrastructure.llm.conversation_parser import (
            parse_conversation_with_llm,
        )

        raw_text = """
        고객센터에 전화가 왔습니다. 상담원이 인사를 하고
        고객이 결제 문제를 말했습니다. 상담원은 확인하겠다고 했습니다.
        """

        with patch(
            "app.infrastructure.llm.conversation_parser._get_parser_chain"
        ) as mock_chain:
            mock_chain.return_value.ainvoke = AsyncMock(return_value=mock_llm_response)

            result = await parse_conversation_with_llm(raw_text)

            assert isinstance(result, Conversation)
            assert result.turn_count >= 1

    @pytest.mark.asyncio
    async def test_parse_handles_llm_error(self):
        """Test that LLM errors are propagated correctly."""
        from app.infrastructure.llm.conversation_parser import (
            parse_conversation_with_llm,
        )

        with patch(
            "app.infrastructure.llm.conversation_parser._get_parser_chain"
        ) as mock_chain:
            mock_chain.return_value.ainvoke = AsyncMock(
                side_effect=Exception("API error")
            )

            with pytest.raises(Exception) as exc_info:
                await parse_conversation_with_llm("some text")

            assert "API error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_parse_empty_text_raises_error(self):
        """Test that empty text raises ValueError."""
        from app.infrastructure.llm.conversation_parser import (
            parse_conversation_with_llm,
        )

        with pytest.raises(ValueError) as exc_info:
            await parse_conversation_with_llm("")

        assert "비어있" in str(exc_info.value) or "empty" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_parse_whitespace_only_raises_error(self):
        """Test that whitespace-only text raises ValueError."""
        from app.infrastructure.llm.conversation_parser import (
            parse_conversation_with_llm,
        )

        with pytest.raises(ValueError):
            await parse_conversation_with_llm("   \n\n   ")

    @pytest.mark.asyncio
    async def test_parse_text_too_long_raises_error(self):
        """Test that text exceeding max length raises ValueError."""
        from app.infrastructure.llm.conversation_parser import (
            MAX_INPUT_LENGTH,
            parse_conversation_with_llm,
        )

        long_text = "a" * (MAX_INPUT_LENGTH + 1)

        with pytest.raises(ValueError) as exc_info:
            await parse_conversation_with_llm(long_text)

        assert "너무 깁니다" in str(exc_info.value)


class TestConvertParsedToConversation:
    """Tests for _convert_to_conversation helper."""

    def test_convert_parsed_messages(self):
        """Test converting ParsedConversation to Conversation."""
        from app.infrastructure.llm.conversation_parser import _convert_to_conversation

        parsed = ParsedConversation(
            messages=[
                ParsedMessage(role="agent", content="Hello"),
                ParsedMessage(role="customer", content="Hi"),
            ]
        )

        result = _convert_to_conversation(parsed)

        assert isinstance(result, Conversation)
        assert result.turn_count == 2
        assert result.turns[0].speaker == "agent"
        assert result.turns[0].message == "Hello"
        assert result.turns[1].speaker == "customer"
        assert result.turns[1].message == "Hi"
