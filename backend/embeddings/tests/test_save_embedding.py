# embeddings/tests/test_save_embedding.py
from embeddings.helpers.helpers_io import save_embedding
from embeddings.models import Embedding
from django.contrib.auth import get_user_model


def test_save_embedding_creates_embedding_for_valid_vector(db):
    user = get_user_model().objects.create(username="testuser")
    vector = [0.1] * 1536
    embedding = save_embedding(user, vector)

    assert embedding is not None
    assert isinstance(embedding, Embedding)
    assert embedding.embedding[:3] == vector[:3]  # rough vector match
