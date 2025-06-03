#!/usr/bin/env python
"""
Verify Embeddings Script

This script validates that the embedding system is working correctly with the
BGE-large model and projection layer.

It checks:
1. Embedding dimensions match OpenAI's (1536)
2. The model initializes correctly
3. Batch processing works
4. The embeddings are normalized properly

Usage:
  python verify_embeddings.py

This will validate the system and print results.
"""

import os
import sys
import numpy as np
import time
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("verify_embeddings")

# Add Django project to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")

# Setup Django
import django

django.setup()

# Now import our modules
from embeddings.sentence_transformer_service import get_sentence_transformer
from embeddings.helpers import generate_embedding
from embeddings.models import EMBEDDING_LENGTH
from embeddings.vector_utils import normalize_vector, cosine_similarity


def verify_dimensions():
    """Verify embedding dimensions match OpenAI's 1536."""
    logger.info("Verifying embedding dimensions...")

    # Test texts
    test_texts = [
        "This is a simple test sentence.",
        "Another test with different content.",
        "A third sample to verify batch processing.",
    ]

    # Direct from transformer service
    transformer = get_sentence_transformer()
    start_time = time.time()
    embeddings = transformer.encode(test_texts)
    elapsed = time.time() - start_time

    # Check dimensions
    logger.info(f"Generated embeddings shape: {embeddings.shape}")
    assert embeddings.shape == (
        len(test_texts),
        EMBEDDING_LENGTH,
    ), f"Expected shape ({len(test_texts)}, {EMBEDDING_LENGTH}), got {embeddings.shape}"
    logger.info(f"✓ Embedding dimensions verified: {EMBEDDING_LENGTH}")
    logger.info(f"✓ Batch encoding works for {len(test_texts)} texts")
    logger.info(
        f"✓ Encoding took {elapsed:.2f} seconds for {len(test_texts)} texts "
        + f"({elapsed/len(test_texts):.2f} seconds per text)"
    )

    # Verify through helpers
    start_time = time.time()
    helper_embedding = generate_embedding(test_texts[0])
    helper_elapsed = time.time() - start_time

    assert helper_embedding.shape == (
        EMBEDDING_LENGTH,
    ), f"Helper embedding should have shape ({EMBEDDING_LENGTH},), got {helper_embedding.shape}"
    logger.info(f"✓ Helper embedding dimension verified: {helper_embedding.shape}")
    logger.info(f"✓ Helper embedding took {helper_elapsed:.2f} seconds")

    return embeddings, helper_embedding


def verify_normalization():
    """Verify embedding normalization works correctly."""
    logger.info("\nVerifying embedding normalization...")

    # Generate a test embedding
    transformer = get_sentence_transformer()
    embedding = transformer.encode("Test normalization")

    # Normalize it
    normalized = normalize_vector(embedding)

    # Check L2 norm (should be 1.0)
    norm = np.linalg.norm(normalized)
    logger.info(f"Normalized vector L2 norm: {norm}")
    assert np.isclose(
        norm, 1.0, atol=1e-6
    ), f"Normalized vector should have L2 norm of 1.0, got {norm}"
    logger.info("✓ Normalization verified (L2 norm = 1.0)")

    return normalized


def verify_similarity():
    """Verify similarity calculations work correctly."""
    logger.info("\nVerifying similarity calculations...")

    # Generate embeddings for related and unrelated texts
    transformer = get_sentence_transformer()

    # Related texts
    related1 = "The quick brown fox jumps over the lazy dog."
    related2 = "A fast brown fox leaped over a sleeping canine."

    # Unrelated text
    unrelated = "Artificial intelligence is transforming technology."

    # Generate embeddings
    emb1 = transformer.encode(related1)
    emb2 = transformer.encode(related2)
    emb3 = transformer.encode(unrelated)

    # Calculate similarities
    sim_related = cosine_similarity(emb1, emb2)
    sim_unrelated = cosine_similarity(emb1, emb3)

    logger.info(f"Similarity between related texts: {sim_related:.4f}")
    logger.info(f"Similarity between unrelated texts: {sim_unrelated:.4f}")

    # Verify related texts are more similar than unrelated
    assert (
        sim_related > sim_unrelated
    ), f"Related texts should have higher similarity ({sim_related}) than unrelated ({sim_unrelated})"
    logger.info("✓ Similarity verification passed (related > unrelated)")

    return sim_related, sim_unrelated


def check_recent_chat_chunks(limit: int = 50):
    """Report chunks used in recent chats that lack embeddings."""
    from django.utils import timezone
    from datetime import timedelta
    from assistants.models.thoughts import AssistantThoughtLog
    from intel_core.models import DocumentChunk

    cutoff = timezone.now() - timedelta(days=1)
    logs = AssistantThoughtLog.objects.filter(created_at__gte=cutoff)
    ids: list[str] = []
    for log in logs:
        details = log.fallback_details or {}
        ids.extend(details.get("chunk_ids", []))

    if not ids:
        logger.info("No recent chunk usage found in thought logs")
        return

    bad = (
        DocumentChunk.objects.filter(id__in=ids)
        .exclude(embedding_status="embedded")
        .values_list("id", "embedding_status")
    )
    if bad:
        logger.warning("\nChunks used without embeddings:")
        for cid, status in bad[:limit]:
            logger.warning(" - %s | status=%s", cid, status)
    else:
        logger.info("All referenced chunks are embedded")


def main():
    """Run all verification checks."""
    logger.info("==== Starting Embedding System Verification ====")
    logger.info(f"Expected embedding dimensions: {EMBEDDING_LENGTH}")

    try:
        # Verify dimensions
        embeddings, helper_embedding = verify_dimensions()

        # Verify normalization
        normalized = verify_normalization()

        # Verify similarity
        sim_related, sim_unrelated = verify_similarity()

        # Report any invalid chunks used recently
        check_recent_chat_chunks()

        logger.info("\n==== All Verification Checks Passed! ====")
        logger.info(f"✓ Embedding dimensions: {EMBEDDING_LENGTH}")
        logger.info(f"✓ Normalization: Working")
        logger.info(f"✓ Similarity calculation: Working")
        logger.info(f"✓ Helper integration: Working")

        return True
    except Exception as e:
        logger.error(f"Verification failed: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
