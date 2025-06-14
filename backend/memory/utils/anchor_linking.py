from __future__ import annotations

from collections import defaultdict
from typing import Optional

from embeddings.helpers.helpers_io import get_embedding_for_text
from embeddings.vector_utils import compute_similarity
from intel_core.models import DocumentChunk, ChunkTag
from memory.models import SymbolicMemoryAnchor, RAGGroundingLog


def _embedding_matches(
    anchor: SymbolicMemoryAnchor, threshold: float = 0.25, limit: int = 5
) -> list[DocumentChunk]:
    try:
        vec = get_embedding_for_text(anchor.label)
    except Exception:
        return []
    if not vec:
        return []

    results: list[tuple[float, DocumentChunk]] = []
    qs = DocumentChunk.objects.filter(embedding__isnull=False).select_related(
        "embedding"
    )
    if anchor.assistant_id:
        doc_ids = anchor.assistant.documents.values_list("id", flat=True)
        qs = qs.filter(document_id__in=list(doc_ids))

    for ch in qs.iterator():
        if not ch.embedding:
            continue
        score = compute_similarity(vec, ch.embedding.vector)
        if score >= threshold:
            results.append((score, ch))

    results.sort(key=lambda x: x[0], reverse=True)
    return [c for _s, c in results[:limit]]


def _log_matches(
    anchor: SymbolicMemoryAnchor, threshold: float = 0.25, limit: int = 5
) -> list[DocumentChunk]:
    score_map: defaultdict[str, list[float]] = defaultdict(list)
    logs = RAGGroundingLog.objects.filter(expected_anchor=anchor.slug)
    for log in logs:
        score = log.adjusted_score or log.corrected_score or log.retrieval_score or 0.0
        for cid in log.used_chunk_ids:
            score_map[cid].append(score)

    if not score_map:
        return []

    chunk_qs = DocumentChunk.objects.filter(id__in=score_map.keys())
    results: list[tuple[float, DocumentChunk]] = []
    for ch in chunk_qs:
        avg = sum(score_map[str(ch.id)]) / len(score_map[str(ch.id)])
        if avg >= threshold:
            results.append((avg, ch))
    results.sort(key=lambda x: x[0], reverse=True)
    return [c for _s, c in results[:limit]]


def relink_anchor_chunks(
    assistant: Optional[object] = None,
    *,
    threshold: float = 0.25,
    purge: bool = False,
    dry_run: bool = False,
    stdout=None,
) -> int:
    """Reconnect anchors to chunks via ChunkTag entries.

    Returns number of ChunkTag links created.
    """
    anchors = SymbolicMemoryAnchor.objects.all()
    if assistant:
        anchors = anchors.filter(assistant=assistant)

    created = 0
    for anchor in anchors:
        chunks = _embedding_matches(anchor, threshold)
        if not chunks:
            chunks = _log_matches(anchor, threshold)
        if not chunks:
            if stdout:
                stdout.write(f"⚠️ no chunks for {anchor.slug}")
            continue
        if purge and not dry_run:
            ChunkTag.objects.filter(chunk__in=chunks, name=anchor.slug).delete()
        for ch in chunks:
            if not ChunkTag.objects.filter(chunk=ch, name=anchor.slug).exists():
                created += 1
                if not dry_run:
                    ChunkTag.objects.create(chunk=ch, name=anchor.slug)
        if stdout and dry_run:
            stdout.write(f"{anchor.slug}: {len(chunks)}")
    return created
