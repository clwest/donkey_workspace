"""
Helper to map model_backend keys to Replicate model slug and version ID.
"""

from typing import Tuple


def get_model_info(model_backend: str) -> Tuple[str, str]:
    """
    Return (model_slug, version_id) for a given model_backend identifier.
    """
    if model_backend == "replicate-standard":
        return (
            "user/image-model",
            "standard-version-id",
        )
    elif model_backend == "replicate-kling":
        return (
            "lucataco/kling-v1.6",
            "bd786ac63d18c4c544e957a06b4cb1d165e0292d8b480d6de10178108331392d",
        )
    raise ValueError(f"Unsupported model backend: {model_backend}")
