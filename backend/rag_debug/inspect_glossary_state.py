"""Simple inspection script for glossary chunk coverage."""

import os
import sys
import django

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
django.setup()

from intel_core.models import DocumentChunk


def run():
    chunks = DocumentChunk.objects.filter(document__title__icontains="solidity")
    gloss = chunks.filter(is_glossary=True).select_related("anchor", "document")
    print(f"📄 Total Solidity chunks: {chunks.count()}")
    print(f"📚 Glossary chunks: {gloss.count()}")
    for c in gloss:
        anchor = c.anchor.slug if c.anchor else "None"
        has_emb = bool(c.embedding_id)
        print(f"- {c.document.title} | anchor={anchor} | score={c.score} | embedded={has_emb}")


if __name__ == "__main__":
    run()
