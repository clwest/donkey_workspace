"""Tests for basic chunking helpers."""

import pytest

from intel_core.utils.enhanced_chunking import _default_chunking


def test_chunking_single_chunk():
    """Text shorter than chunk_size should return one chunk unchanged."""
    text = "hello world"
    chunks = _default_chunking(text)
    assert chunks == [text]


def test_chunking_boundary_conditions():
    """Generated chunks should overlap by approximately 300 characters."""
    # Create text slightly larger than chunk_size so two chunks are produced
    sample = "a" * 1700
    chunks = _default_chunking(sample)

    assert len(chunks) >= 2
    # Overlap should be present
    overlap = set(chunks[0][-300:]) & set(chunks[1][:300])
    assert overlap
