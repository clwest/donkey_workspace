from django.contrib.contenttypes.models import ContentType
from embeddings.models import Embedding
from intel_core.models import DocumentChunk
from memory.models import MemoryEntry
from prompts.models import Prompt


def fix_embedding_links(limit=None):
    """Scan embeddings and repair content links in place.

    Returns a dictionary with scanned, fixed and skipped counts.
    """
    ct_chunk = ContentType.objects.get_for_model(DocumentChunk)
    ct_memory = ContentType.objects.get_for_model(MemoryEntry)
    ct_prompt = ContentType.objects.get_for_model(Prompt)
    ct_map = {
        "documentchunk": ct_chunk,
        "memoryentry": ct_memory,
        "prompt": ct_prompt,
    }
    qs = Embedding.objects.select_related("content_type")
    if limit:
        qs = qs.order_by("id")[:limit]

    scanned = 0
    fixed = 0
    skipped = 0
    for emb in qs:
        scanned += 1
        obj = emb.content_object
        # Try resolving from content_id if object missing
        if obj is None and emb.content_id and ":" in emb.content_id:
            model, obj_id = emb.content_id.split(":", 1)
            ct_guess = ct_map.get(model.lower())
            if ct_guess:
                obj = ct_guess.model_class().objects.filter(id=obj_id).first()
                if obj:
                    emb.content_type = ct_guess
                    emb.object_id = str(obj.id)
        if not obj:
            skipped += 1
            continue

        expected_ct = ContentType.objects.get_for_model(obj.__class__)
        expected_cid = f"{expected_ct.model}:{obj.id}"
        changed = False
        if emb.content_type != expected_ct:
            emb.content_type = expected_ct
            changed = True
        if emb.object_id != str(obj.id):
            emb.object_id = str(obj.id)
            changed = True
        if emb.content_id != expected_cid:
            emb.content_id = expected_cid
            changed = True
        if changed:
            emb.save(update_fields=["content_type", "object_id", "content_id"])
            fixed += 1
    return {"scanned": scanned, "fixed": fixed, "skipped": skipped}
