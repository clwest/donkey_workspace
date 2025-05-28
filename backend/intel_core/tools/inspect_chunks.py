def inspect_orphaned_chunks():
    from intel_core.models import DocumentChunk

    chunks = DocumentChunk.objects.filter(embedding__isnull=True)
    for c in chunks:
        preview = c.text[:120].replace("\n", " ")
        print(f"❌ Chunk {c.order} | Document: {c.document.title} | Score: {c.score}")
        print(f"Text: {preview}")
