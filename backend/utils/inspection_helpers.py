"""Helpers for diagnostic inspection commands."""

from typing import Iterable


def bool_icon(value: bool) -> str:
    """Return a green check or red X icon for booleans."""
    return "✅" if value else "❌"


def print_glossary_debug_table(
    stdout,
    anchor_slug: str,
    chunks: Iterable,
    match_info: dict | None = None,
) -> None:
    """Print a diagnostic table for glossary chunks."""
    header = (
        f"📎 Glossary Anchor: {anchor_slug}\n"
        f"{'ID':<6}{'Glossary':<10}{'Embedded':<10}{'Fingerprint':<14}{'Score':<7}Doc Title"
    )
    stdout.write(header)
    stdout.write("* = retagged match")

    missing_emb = 0
    missing_fingerprint = 0
    missing_score = 0
    missing_glossary = 0
    total = 0

    for chunk in chunks:
        total += 1
        has_emb = chunk.embedding_id is not None
        has_fp = bool(getattr(chunk, "fingerprint", ""))
        score_val = chunk.score if chunk.score is not None else 0.0
        retagged = anchor_slug in getattr(chunk, "matched_anchors", []) and (
            not chunk.anchor or chunk.anchor.slug != anchor_slug
        )

        if not has_emb:
            missing_emb += 1
        if not has_fp:
            missing_fingerprint += 1
        if score_val == 0:
            missing_score += 1
        if not chunk.is_glossary:
            missing_glossary += 1

        prefix = "*" if retagged else ""
        via = ""
        if match_info:
            via = match_info.get(str(chunk.id), "")
        stdout.write(
            f"{prefix}{chunk.order:<5}"  # type: ignore[attr-defined]
            f"{bool_icon(chunk.is_glossary):<10}"
            f"{bool_icon(has_emb):<10}"
            f"{bool_icon(has_fp):<14}"
            f"{score_val:<7.2f}"
            f"{chunk.document.title}" + (f" via={via}" if via else "")
        )

    stdout.write("\n")
    stdout.write(f"Total chunks found for anchor: {total}")
    stdout.write(f"Chunks missing is_glossary flag: {missing_glossary}")
    stdout.write(f"Chunks missing embeddings: {missing_emb}")
    stdout.write(f"Chunks missing fingerprint: {missing_fingerprint}")
    stdout.write(f"Chunks with score 0: {missing_score}")

    if missing_emb or missing_score:
        stdout.write(
            "⚠️ Recommendation: run embed_missing_chunks or scoring tasks to complete metadata."
        )
