import sys
import types

# Stub openai module for testing if not installed
_openai_mod = types.ModuleType("openai")


class _EmbeddingStub:
    @staticmethod
    def create(*args, **kwargs):
        raise NotImplementedError("stub")


_openai_mod.Embedding = _EmbeddingStub
sys.modules["openai"] = _openai_mod

import pytest
import logging
from unittest import mock
import openai
import embeddings.helpers.helpers_processing as hp
from embeddings.helpers.helpers_processing import (
    generate_embedding,
    retry_with_backoff,
)
from embeddings.vector_utils import compute_similarity


def test_generate_embedding_success(monkeypatch):
    # Mock OpenAI embedding API to return a known embedding
    fake_response = {"data": [{"embedding": [0.1, 0.2, 0.3]}]}
    # Replace Embedding.create with our fake
    monkeypatch.setattr(
        openai.Embedding, "create", mock.Mock(return_value=fake_response)
    )
    # No delays or jitter during test
    monkeypatch.setattr(hp.time, "sleep", lambda x: None)
    monkeypatch.setattr(hp.random, "uniform", lambda a, b: 0)
    emb = generate_embedding("test text", model="test-model")
    assert emb == [0.1, 0.2, 0.3]
    openai.Embedding.create.assert_called_once_with(
        model="test-model", input="test text"
    )


def test_generate_embedding_api_failure(monkeypatch, caplog):
    # Simulate API always failing to trigger fallback
    def fake_create(**kwargs):
        raise ValueError("API error")

    monkeypatch.setattr(openai.Embedding, "create", fake_create)
    # Disable actual sleep
    monkeypatch.setattr(hp.time, "sleep", lambda x: None)
    monkeypatch.setattr(hp.random, "uniform", lambda a, b: 0)
    caplog.set_level(logging.ERROR, logger="embeddings")
    emb = generate_embedding("will fail")
    assert emb is None
    # Should log an error about generating embedding
    assert "Error generating embedding for text" in caplog.text


@pytest.mark.parametrize(
    "vec1,vec2,expected",
    [
        ([1, 0, 0], [1, 0, 0], 1.0),  # identical vectors
        ([1, 1], [1, -1], 0.0),  # opposite direction clamped to 0
    ],
)
def test_compute_similarity_normal(vec1, vec2, expected):
    sim = compute_similarity(vec1, vec2)
    assert pytest.approx(sim, rel=1e-6) == expected


def test_compute_similarity_mismatched_or_empty(caplog):
    caplog.set_level(logging.ERROR, logger="embeddings")
    # Mismatched lengths
    sim1 = compute_similarity([1, 2], [1, 2, 3])
    assert sim1 == 0.0
    assert "Vectors must be non-empty and of same length" in caplog.text
    caplog.clear()
    # Empty vectors
    sim2 = compute_similarity([], [])
    assert sim2 == 0.0
    assert "Vectors must be non-empty and of same length" in caplog.text


def test_retry_with_backoff_success(monkeypatch, caplog):
    # Patch sleep and jitter to speed up test
    monkeypatch.setattr(hp.time, "sleep", lambda x: None)
    monkeypatch.setattr(hp.random, "uniform", lambda a, b: 0)
    caplog.set_level(logging.WARNING, logger="embeddings")
    calls = []

    # Flaky function: fails first time, succeeds second
    def flaky(x):
        calls.append(x)
        if len(calls) < 2:
            raise RuntimeError("intermittent failure")
        return "ok"

    result = retry_with_backoff(flaky, "arg1")
    assert result == "ok"
    # Ensure function was retried once
    assert len(calls) == 2
    # Warning for first retry should be logged
    assert "Retry 1/3 for flaky" in caplog.text


def test_retry_with_backoff_failure_exceeds(monkeypatch, caplog):
    # Patch sleep and jitter
    monkeypatch.setattr(hp.time, "sleep", lambda x: None)
    monkeypatch.setattr(hp.random, "uniform", lambda a, b: 0)
    caplog.set_level(logging.ERROR, logger="embeddings")

    # Function that always fails
    def always_fail():
        raise ValueError("fail forever")

    # Expect ValueError after retries exceeded
    with pytest.raises(ValueError):
        retry_with_backoff(always_fail, retries=2, base_delay=0.01)
    # Error log for final failure should be present
    assert "Function always_fail failed after 2 retries" in caplog.text
