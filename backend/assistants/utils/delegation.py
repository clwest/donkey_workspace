"""Utilities for spawning delegated assistants."""

from __future__ import annotations

from typing import Optional, Union

from assistants.models import (
    Assistant,
    ChatSession,
    DelegationEvent,
    AssistantObjective,
    TokenUsage,
)
from assistants.helpers.reflection_helpers import reflect_on_delegation
from assistants.helpers.mood import get_session_mood, map_mood_to_tone
from memory.models import MemoryEntry
from mcp_core.models import NarrativeThread
from project.models import Project
from prompts.models import Prompt
from tools.models import Tool


def should_delegate(
    assistant: Assistant,
    token_usage: Optional[TokenUsage],
    feedback_flag: Optional[str] = None,
) -> bool:
    """Return True if delegation should occur based on thresholds."""

    if assistant.delegation_threshold_tokens and token_usage:
        if token_usage.total_tokens > assistant.delegation_threshold_tokens:
            return True

    if feedback_flag and assistant.auto_delegate_on_feedback:
        return feedback_flag in assistant.auto_delegate_on_feedback

    return False


from core.services.assistant_service import spawn_delegated_assistant
