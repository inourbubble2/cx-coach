"""Conversation domain models.

This module contains the core entities for counseling conversations.
"""

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class Turn(BaseModel):
    """A single turn in a conversation.

    Represents one utterance from either the agent or the customer
    in a counseling conversation.
    """

    speaker: Literal["agent", "customer"]
    message: str
    timestamp: datetime | None = None


class Conversation(BaseModel):
    """A complete counseling conversation.

    Contains all turns between an agent and customer along with
    optional metadata about the conversation.
    """

    id: uuid.UUID | None = None
    created_at: datetime | None = None
    turns: list[Turn]
    metadata: dict | None = None

    @property
    def turn_count(self) -> int:
        """Return the total number of turns in the conversation."""
        return len(self.turns)

    @property
    def agent_turns(self) -> list[Turn]:
        """Return all turns by the agent."""
        return [t for t in self.turns if t.speaker == "agent"]

    @property
    def customer_turns(self) -> list[Turn]:
        """Return all turns by the customer."""
        return [t for t in self.turns if t.speaker == "customer"]
