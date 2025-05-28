from mcp_core.utils.tagging import infer_tags_from_text
from mcp_core.utils.auto_tag_from_embedding import auto_tag_from_embedding
from mcp_core.models import Tag
from memory.utils.tag_utils import normalize_tag_name


def tag_thought_content(content: str, top_k=5) -> list[Tag]:
    tag_names = set()

    # LLM tags
    try:
        llm_tags = infer_tags_from_text(content)
        tag_names.update(llm_tags)
    except Exception:
        pass

    # Embedding-based tags
    try:
        embed_matches = auto_tag_from_embedding(content, top_k=top_k)
        tag_names.update([match["tag"] for match in embed_matches])
    except Exception:
        pass

    # Get/create tags in DB using normalized slug lookup
    tag_objs = []
    for name in tag_names:
        norm_name, slug = normalize_tag_name(name)
        obj, _ = Tag.objects.get_or_create(slug=slug, defaults={"name": norm_name})
        tag_objs.append(obj)

    return tag_objs
