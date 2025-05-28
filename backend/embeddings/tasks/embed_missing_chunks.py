"""Command-line helper to embed all DocumentChunks lacking embeddings."""

import os
import sys
import django

# Django setup
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
django.setup()

from intel_core.models import DocumentChunk
from embeddings.tasks import embed_and_store


def run():
    chunks = DocumentChunk.objects.filter(embedding__isnull=True)
    print(f"🔍 Found {chunks.count()} chunks missing embeddings.")
    for chunk in chunks:
        preview = chunk.text[:60].replace("\n", " ")
        print(f"📌 Embedding chunk {chunk.id} ({preview})")
        embed_and_store.delay(str(chunk.id))


if __name__ == "__main__":
    run()
