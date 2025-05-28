import os
import sys
import django

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
django.setup()

from intel_core.models import DocumentChunk
from embeddings.document_services.chunking import clean_and_score_chunk


def run():
    total = 0
    removed = 0
    for chunk in DocumentChunk.objects.all():
        info = clean_and_score_chunk(chunk.text, chunk_index=chunk.order)
        if not info.get("keep"):
            if chunk.embedding:
                chunk.embedding.delete()
            chunk.delete()
            removed += 1
            continue
        chunk.score = info.get("score", 0.0)
        chunk.quality_notes = info.get("origin", "recleaned")
        chunk.save(update_fields=["score", "quality_notes"])
        total += 1
    print(f"Re-cleaned {total} chunks, removed {removed} bad chunks")


if __name__ == "__main__":
    run()
