from __future__ import annotations

import re
from collections import Counter, defaultdict
from typing import Optional

from django.utils.text import slugify

from assistants.models import Assistant
from intel_core.models import DocumentChunk
from memory.models import SymbolicMemoryAnchor, RAGPlaybackLog

TOKEN_RE = re.compile(r"[a-zA-Z0-9-]{3,}")


def _tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


def rebuild_anchors_from_chunks(
    assistant: Optional[Assistant] = None,
    *,
    threshold: float = 0.25,
    top_n: int = 5,
    doc_type: Optional[str] = None,
    replace: bool = False,
    stdout=None,
) -> int:
    """Generate SymbolicMemoryAnchor terms from high-scoring RAG chunks."""

    logs = RAGPlaybackLog.objects.all()
    if assistant:
        logs = logs.filter(assistant=assistant)

    score_map: defaultdict[str, list[float]] = defaultdict(list)
    for pb in logs:
        for info in pb.chunks:
            score = (
                info.get("final_score")
                or info.get("score")
                or info.get("match_score")
                or 0.0
            )
            if score < threshold:
                continue
            cid = info.get("id") or info.get("chunk_id")
            if cid:
                score_map[str(cid)].append(float(score))

    if not score_map:
        if stdout:
            stdout.write("No matching chunks found\n")
        return 0

    chunk_qs = DocumentChunk.objects.filter(id__in=score_map.keys()).select_related(
        "document"
    )
    counter: Counter[str] = Counter()

    for chunk in chunk_qs:
        if doc_type and getattr(chunk.document, "source_type", None) != doc_type:
            continue
        tokens = _tokenize(chunk.text)
        avg_score = sum(score_map[str(chunk.id)]) / len(score_map[str(chunk.id)])
        for tok in tokens:
            counter[tok] += avg_score

    if not counter:
        if stdout:
            stdout.write("No tokens extracted\n")
        return 0

    terms = [term for term, _ in counter.most_common(top_n)]

    if replace:
        qs = SymbolicMemoryAnchor.objects.filter(source="auto_chunk")
        if assistant:
            qs = qs.filter(assistant=assistant)
        qs.delete()

    created = 0
    for term in terms:
        slug = slugify(term)
        if SymbolicMemoryAnchor.objects.filter(slug=slug).exists():
            continue
        anchor = SymbolicMemoryAnchor.objects.create(
            slug=slug,
            label=term.title(),
            source="auto_chunk",
            created_from="chunk_rebuild",
            assistant=assistant,
            memory_context=getattr(assistant, "memory_context", None),
        )
        created += 1
        if stdout:
            stdout.write(f"Added {anchor.label}\n")

    return created
