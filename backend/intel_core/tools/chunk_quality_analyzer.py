from intel_core.models import DocumentChunk
from embeddings.document_services.chunking import clean_and_score_chunk


def run_chunk_quality_report():
    results = []
    for idx, chunk in enumerate(DocumentChunk.objects.all()):
        result = clean_and_score_chunk(chunk.text, chunk_index=idx)
        results.append(
            {
                "chunk_id": str(chunk.id),
                "score": result["score"],
                "keep": result["keep"],
                "preview": result["text"][:80],
            }
        )

    results.sort(key=lambda r: r["score"], reverse=True)
    # The emoji was previously expressed using surrogate pair escapes which can
    # raise UnicodeEncodeError in some environments. Using the actual emoji
    # character ensures proper encoding on UTF-8 terminals.
    print("📊 Chunk Quality Report:")
    for r in results:
        print(f"{r['score']:.2f} | keep={r['keep']} | {r['preview']}...")
