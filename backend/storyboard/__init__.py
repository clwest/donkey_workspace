"""Storyboard utilities exposed at the package level."""

__all__ = ["UnifiedStoryboardController"]


def __getattr__(name):
    if name == "UnifiedStoryboardController":
        # Import lazily to avoid Django app loading issues
        from .controllers import UnifiedStoryboardController

        return UnifiedStoryboardController
    raise AttributeError(name)
