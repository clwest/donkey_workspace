from intel_core.models import DocumentChunk
from embeddings.document_services.chunking import clean_and_score_chunk


def run_chunk_quality_report():
    results = []
    for chunk in DocumentChunk.objects.all():
        result = clean_and_score_chunk(chunk.text)
        results.append(
            {
                "chunk_id": str(chunk.id),
                "score": result["score"],
                "keep": result["keep"],
                "preview": result["text"][:80],
            }
        )

    results.sort(key=lambda r: r["score"], reverse=True)
    print("\ud83d\udcca Chunk Quality Report:")
    for r in results:
        print(f"{r['score']:.2f} | keep={r['keep']} | {r['preview']}...")
