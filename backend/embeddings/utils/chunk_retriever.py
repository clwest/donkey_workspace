from django.conf import settings


def should_embed_chunk(chunk) -> bool:
    """Return True if the chunk should be embedded."""
    if getattr(chunk, "force_embed", False):
        return True
    threshold = getattr(settings, "CHUNK_EMBED_SCORE_THRESHOLD", 0.25)
    return chunk.score is None or chunk.score >= threshold
