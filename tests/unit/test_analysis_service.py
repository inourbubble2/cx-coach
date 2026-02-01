"""Unit tests for analysis service."""

import uuid
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.application.analysis_service import analyze_conversation
from app.domain import Conversation, Turn


@pytest.mark.asyncio
async def test_analyze_conversation():
    """Test that analyze_conversation calls the graph and saves conversation."""
    conversation = Conversation(turns=[Turn(speaker="agent", message="hello")])

    # Create a mock result that has model_copy method (like a Pydantic model)
    mock_result = MagicMock()
    mock_result.model_copy.return_value = mock_result

    mock_state = {"analysis_result": mock_result}

    # Create a saved conversation with an id
    saved_conversation = Conversation(
        id=uuid.uuid4(),
        turns=[Turn(speaker="agent", message="hello")],
    )

    # Mock the graph invocation
    with patch(
        "app.application.analysis_service.analysis_graph.ainvoke",
        new_callable=AsyncMock,
    ) as mock_invoke:
        mock_invoke.return_value = mock_state

        # Mock conversation save
        with patch(
            "app.application.analysis_service._save_conversation_to_db",
            new_callable=AsyncMock,
        ) as mock_save_conv:
            mock_save_conv.return_value = saved_conversation

            # Mock DB save to avoid errors
            with patch(
                "app.application.analysis_service._save_result_to_db",
                new_callable=AsyncMock,
            ):
                result = await analyze_conversation(conversation, use_faq=False)

                assert result == mock_result
                mock_invoke.assert_called_once()
                mock_save_conv.assert_called_once_with(conversation)
                # Verify conversation_id was linked
                mock_result.model_copy.assert_called_once()
