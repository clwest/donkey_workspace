from __future__ import annotations

from typing import List

from tags.models import Tag


def resolve_tags_from_names(
    tag_names: List[str], category: str = "reflection"
) -> List[Tag]:
    """Return Tag instances for the provided tag names."""
    tags: List[Tag] = []
    for name in tag_names:
        tag, _ = Tag.objects.get_or_create(name=name, defaults={"category": category})
        tags.append(tag)
    return tags


def tag_reflection(reflection) -> None:
    """Generate and apply tags for a given AssistantReflectionLog."""
    from embeddings.helpers.helper_tagging import generate_tags_for_memory

    tag_names = generate_tags_for_memory(reflection.summary)
    tags = resolve_tags_from_names(tag_names)
    reflection.tags.set(tags)
