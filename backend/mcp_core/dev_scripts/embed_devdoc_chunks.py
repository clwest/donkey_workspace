# mcp_core/scripts/embed_and_chunk_devdocs.py

import os
import django
import sys

# Setup Django
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
django.setup()

from mcp_core.models import DevDoc
from embeddings.models import Embedding
from embeddings.document_services.chunking import generate_chunks
from embeddings.helpers.helpers_processing import generate_embedding
from django.contrib.contenttypes.models import ContentType

def auto_chunk_and_embed_devdocs():
    content_type = ContentType.objects.get_for_model(DevDoc)

    for doc in DevDoc.objects.all():
        print(f"📄 Processing: {doc.slug}")

        chunks = generate_chunks(doc.content)
        print(f"  ✂️ {len(chunks)} chunks")

        for chunk in chunks:
            try:
                vector = generate_embedding(chunk)
                if not vector:
                    print("  ❌ Failed to generate embedding for chunk")
                    continue

                Embedding.objects.create(
                    content=chunk,
                    embedding=vector,
                    source_type="devdoc-chunk",
                    content_type=content_type,
                    object_id=doc.id,
                )
                print("  ✅ Embedded chunk")
            except Exception as e:
                print(f"  ⚠️ Error embedding chunk: {e}")


if __name__ == "__main__":
    auto_chunk_and_embed_devdocs()