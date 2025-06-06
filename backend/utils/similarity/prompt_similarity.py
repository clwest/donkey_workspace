"""Utilities for scoring differences between prompt texts."""

from __future__ import annotations


def score_reflection_diff(original: str, replayed: str) -> float:
    """Return a score indicating how similar two reflection prompts are.

    A higher score means the prompts are more similar. This stub currently
    returns ``0.0`` and should be replaced with a real implementation
    when prompt similarity scoring is needed.
    """
    # TODO: implement actual similarity scoring
    return 0.0
