"""
Helper functions to manipulate prompts based on ThemeHelper presets.
"""

from typing import Optional
from images.models import ThemeHelper


def get_prompt_for_theme(theme: ThemeHelper, base_prompt: str) -> str:
    """
    Append the theme's prompt to the base prompt for AI generation.
    """
    # Combine base prompt and theme-specific prompt
    return f"{base_prompt}, {theme.prompt}"


def get_negative_prompt_for_theme(theme: ThemeHelper) -> Optional[str]:
    """
    Return the negative prompt for the theme, if any.
    """
    return theme.negative_prompt or None
