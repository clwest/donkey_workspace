import math
import sys
import types
import logging
import pytest

# Stub out external dependencies before imports
import types
import sys

# Stub openai to allow helpers_processing import
sys.modules.setdefault("openai", types.ModuleType("openai"))
sys.modules["openai"].Embedding = type(
    "Embedding", (object,), {"create": staticmethod(lambda *a, **k: None)}
)
# Stub characters.models module to avoid real Django imports
fake_pkg = types.ModuleType("characters")
# Mark as package
fake_pkg.__path__ = []
sys.modules["characters"] = fake_pkg
fake_ch_mod = types.ModuleType("characters.models")


# Placeholder CharacterTrainingProfile for similarity tests
class CharacterTrainingProfileStub:
    pass


fake_ch_mod.CharacterTrainingProfile = CharacterTrainingProfileStub
sys.modules["characters.models"] = fake_ch_mod

import os
import sys
import types
import importlib.util

# Stub openai to allow module import
sys.modules.setdefault("openai", types.ModuleType("openai"))

# Load helpers_processing directly to avoid package imports
hp_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "helpers", "helpers_processing.py")
)
spec = importlib.util.spec_from_file_location("helpers_processing", hp_path)
hp = importlib.util.module_from_spec(spec)
sys.modules["helpers_processing"] = hp
spec.loader.exec_module(hp)
from embeddings.vector_utils import compute_similarity
find_similar_characters = hp.find_similar_characters


class FakeChar:
    def __init__(self, id, name):
        self.id = id
        self.name = name


class FakeTP:
    def __init__(self, character, similarity=None, embedding=None):
        self.character = character
        self.similarity = similarity
        if embedding is not None:
            self.embedding = embedding


def test_compute_similarity_identical_and_orthogonal():
    # Identical vectors -> similarity ~1.0
    assert compute_similarity([1, 0, 0], [1, 0, 0]) == pytest.approx(1.0)
    # Orthogonal vectors -> similarity ~0.0
    assert compute_similarity([1, 0], [0, 1]) == pytest.approx(0.0)


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


@pytest.mark.parametrize(
    "vector, profiles, expected_ids",
    [
        # vector doesn't matter for DB path since we set fake similarities
        (
            [0, 0],
            [
                FakeTP(FakeChar(1, "A"), similarity=0.8),
                FakeTP(FakeChar(2, "B"), similarity=0.5),
                FakeTP(FakeChar(3, "C"), similarity=0.9),
            ],
            [3, 1],
        ),
    ],
)
def test_find_similar_characters_db(monkeypatch, vector, profiles, expected_ids):
    # Simulate PGVector path
    monkeypatch.setattr(hp, "PGVECTOR_AVAILABLE", True)
    # Ensure CosineDistance exists
    monkeypatch.setattr(hp, "CosineDistance", lambda f, v: None)

    # Fake QuerySet with annotate and order_by
    class FakeQS:
        def __init__(self, items):
            self.items = items

        def annotate(self, **kwargs):
            return self

        def order_by(self, key):
            return sorted(self.items, key=lambda x: x.similarity, reverse=True)

        def __getitem__(self, slc):
            return self.order_by(None)[slc]

    # Monkeypatch the manager
    import characters.models as ch

    class FakeManager:
        def filter(self, **kwargs):
            return FakeQS(profiles)

    monkeypatch.setattr(
        ch.CharacterTrainingProfile, "objects", FakeManager(), raising=False
    )
    # Run
    results = find_similar_characters(vector, top_k=2)
    # Verify ordering and ids
    assert [r["id"] for r in results] == expected_ids
    # Verify scores preserved
    assert [r["score"] for r in results] == [
        p.similarity
        for p in sorted(profiles, key=lambda x: x.similarity, reverse=True)[:2]
    ]


def test_find_similar_characters_fallback(monkeypatch):
    # Simulate fallback path
    monkeypatch.setattr(hp, "PGVECTOR_AVAILABLE", False)
    # Fake profiles with embeddings
    profiles = [
        FakeTP(FakeChar(1, "A"), embedding=[1, 0]),  # sim=1.0
        FakeTP(FakeChar(2, "B"), embedding=[0, 1]),  # sim=0.0
        FakeTP(FakeChar(3, "C"), embedding=[1, 1]),  # sim=~0.707
    ]

    # Fake manager with filter/exclude
    class FakeManager:
        def filter(self, **kwargs):
            return self

        def exclude(self, **kwargs):
            return profiles

    import characters.models as ch

    monkeypatch.setattr(
        ch.CharacterTrainingProfile, "objects", FakeManager(), raising=False
    )
    # Run query
    results = find_similar_characters([1, 0], top_k=2)
    # Compute expected scores
    exp_scores = [compute_similarity([1, 0], p.embedding) for p in profiles]
    # Sort descending and take top2
    sorted_profiles = sorted(
        zip(profiles, exp_scores), key=lambda x: x[1], reverse=True
    )[:2]
    # Check order
    assert [r["id"] for r in results] == [p.character.id for p, s in sorted_profiles]
    # Check scores
    assert [r["score"] for r in results] == [
        pytest.approx(s) for p, s in sorted_profiles
    ]


def test_find_similar_characters_no_models(monkeypatch, caplog):
    # Simulate missing characters.models import
    caplog.set_level(logging.ERROR, logger="embeddings")
    monkeypatch.setitem(sys.modules, "characters.models", None)
    results = find_similar_characters([1, 2], top_k=3)
    assert results == []
    assert "characters.models not available" in caplog.text
