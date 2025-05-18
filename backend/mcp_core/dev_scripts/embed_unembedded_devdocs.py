import os
import sys
import django

# Django setup
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
django.setup()

# Imports
from intel_core.models import Document
from embeddings.helpers.helpers_processing import generate_embedding
from embeddings.helpers.helpers_io import save_embedding

print("🧬 Embedding unembedded Documents...")

count = 0
for doc in Document.objects.all():
    if doc.status == "completed" and getattr(doc, "embedding", None):
        continue  # Already embedded

    text = getattr(doc, "full_text", None) or getattr(doc, "summary", None) or getattr(doc, "content", None)
    if not text:
        print(f"⚠️ Skipping {doc.title} — no usable text to embed")
        continue

    embedding = generate_embedding(text)
    if embedding:
        save_embedding(doc, embedding)
        count += 1
        print(f"✅ Embedded: {doc.title}")
    else:
        print(f"❌ Failed to generate embedding for: {doc.title}")

print(f"🎉 Done! Embedded {count} new documents.")