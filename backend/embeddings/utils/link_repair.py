


def fix_embedding_links(limit=None, *, dry_run: bool = False, include_memory: bool = False):
    from django.contrib.contenttypes.models import ContentType
    from embeddings.models import Embedding
    from intel_core.models import DocumentChunk, Document
    from memory.models import MemoryEntry
    from prompts.models import Prompt
    from assistants.models import AssistantReflectionLog, AssistantThoughtLog
    from mcp_core.models import DevDoc
    """Scan embeddings and repair content links in place.

    Returns a dictionary with scanned, fixed and skipped counts.
    """
    ct_chunk = ContentType.objects.get_for_model(DocumentChunk)
    ct_prompt = ContentType.objects.get_for_model(Prompt)
    ct_doc = ContentType.objects.get_for_model(Document)
    ct_reflection = ContentType.objects.get_for_model(AssistantReflectionLog)
    ct_thought = ContentType.objects.get_for_model(AssistantThoughtLog)
    ct_devdoc = ContentType.objects.get_for_model(DevDoc)

    ct_map = {
        "documentchunk": ct_chunk,
        "prompt": ct_prompt,
        "document": ct_doc,
        "assistantreflectionlog": ct_reflection,
        "assistantthoughtlog": ct_thought,
        "devdoc": ct_devdoc,
    }

    if include_memory:
        ct_memory = ContentType.objects.get_for_model(MemoryEntry)
        ct_map["memoryentry"] = ct_memory

    print(f"🤓 Fixing embeddings for models: {list(ct_map.keys())}")

    qs = Embedding.objects.select_related("content_type")
    if limit:
        qs = qs.order_by("id")[:limit]

    scanned = 0
    fixed = 0
    skipped = 0
    for emb in qs:
        scanned += 1
        obj = emb.content_object

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
            print(f"🪨 Orphan embedding {emb.id} (no object)")
            continue

        expected_ct = ContentType.objects.get_for_model(obj.__class__)
        expected_cid = f"{expected_ct.model}:{obj.id}"
        changed = False

        if emb.content_type != expected_ct:
            print(f"❗ CT mismatch: {emb.content_type} vs {expected_ct}")
            emb.content_type = expected_ct
            changed = True
        if str(emb.object_id) != str(obj.id):
            print(f"❗ OID mismatch: {emb.object_id} vs {obj.id}")
            emb.object_id = str(obj.id)
            changed = True
        if emb.content_id != expected_cid:
            print(f"❗ CID mismatch: {emb.content_id} vs {expected_cid}")
            emb.content_id = expected_cid
            changed = True

        if changed:
            if not dry_run:
                emb.save(update_fields=["content_type", "object_id", "content_id"])
            fixed += 1
        else:
            print(f"✅ No change needed for {emb.id} — expected {expected_cid}")

    return {"scanned": scanned, "fixed": fixed, "skipped": skipped}
