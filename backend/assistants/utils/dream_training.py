from __future__ import annotations

import random
from typing import Dict

from assistants.models.assistant import Assistant
from assistants.models.thoughts import AssistantThoughtLog


def dream_training_scenario(assistant: Assistant) -> Dict[str, str]:
    """Generate a symbolic dream training scenario for the assistant."""

    memories = (
        AssistantThoughtLog.objects.filter(assistant=assistant)
        .order_by("-created_at")
        .values_list("thought", flat=True)[:3]
    )
    myth = (
        assistant.myth_layers.filter(archived=False).order_by("-created_at").first()
    )
    base = "\n".join(memories)
    if myth:
        base += f"\n{myth.summary}"
    challenge = f"Traverse the labyrinth of echoes carrying the wisdom: {base[:120]}..."
    return {
        "challenge": challenge,
        "objective": "Interpret the symbols and record your reflection",
    }
