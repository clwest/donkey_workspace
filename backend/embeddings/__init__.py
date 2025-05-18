"""
Embeddings Package

This package provides functionality for generating, storing, and retrieving
embeddings for various content types in the application.
"""

# Don't import directly to avoid circular imports
# Instead, provide functions to lazily import when needed


def get_generate_embedding():
    from .helpers import generate_embedding

    return generate_embedding


def get_save_embedding():
    from .helpers import save_embedding

    return save_embedding


def get_normalize_vector():
    from .vector_utils import normalize_vector

    return normalize_vector


def get_cosine_similarity():
    from .vector_utils import cosine_similarity

    return cosine_similarity


# Empty __all__ to prevent automatic imports
__all__ = []
