"""Utility to retroactively link glossary anchors to document chunks."""

import logging
from django.db.models import Q

logger = logging.getLogger("chunk_patch")

ANCHOR_TERMS = [
    {"slug": "smart-contract", "label": "Smart Contract"},
    {"slug": "solidity", "label": "Solidity"},
    {"slug": "bytecode", "label": "Bytecode"},
    {"slug": "evm", "label": "Ethereum Virtual Machine (EVM)"},
    {"slug": "abi", "label": "Application Binary Interface (ABI)"},
    {"slug": "compiler", "label": "Solidity Compiler"},
    {"slug": "deployment", "label": "Contract Deployment"},
]


def patch_chunks():
    """Attach anchors to existing chunks and mark them as glossary entries."""
    from intel_core.models import DocumentChunk
    from memory.models import SymbolicMemoryAnchor

    patched = 0
    for term in ANCHOR_TERMS:
        anchor = SymbolicMemoryAnchor.objects.filter(slug=term["slug"]).first()
        if not anchor:
            logger.warning(f"Anchor {term['slug']} not found, skipping")
            continue

        query = Q(text__icontains=term["slug"]) | Q(text__icontains=term["label"])
        query &= Q(document__title__icontains="solidity") | Q(document__title__icontains="smart")
        chunks = DocumentChunk.objects.filter(query, is_glossary=False)

        for chunk in chunks:
            before = chunk.score
            had_embedding = bool(chunk.embedding_id)
            chunk.is_glossary = True
            chunk.anchor = anchor
            if chunk.score < 0.4:
                chunk.score = 0.4
            chunk.save()
            patched += 1
            logger.info(
                f"{chunk.document.title} | anchor={anchor.slug} | score {before}->{chunk.score} | embedding_present={had_embedding}"
            )
    logger.info(f"Patched {patched} chunks")
    return patched


if __name__ == "__main__":
    import os
    import sys
    import django

    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
    django.setup()

    patch_chunks()
