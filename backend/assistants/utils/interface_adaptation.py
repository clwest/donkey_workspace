from typing import Any, Dict


def compute_adaptation_state(assistant, codex_pressure: float = 1.0, directive_state: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Return basic interface adaptation values."""
    return {
        "panel_visibility": "default",
        "ritual_display_priority": 1.0 if codex_pressure > 0 else 0.5,
        "ui_tone": assistant.tone or "neutral",
    }
