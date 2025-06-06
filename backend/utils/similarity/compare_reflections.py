from __future__ import annotations
from difflib import HtmlDiff, SequenceMatcher
from typing import List, Dict

from intel_core.utils.glossary_tagging import _match_anchor
from memory.models import SymbolicMemoryAnchor


def compare_reflections(original: str, replayed: str) -> Dict[str, object]:
    """Return diff info and glossary drift stats between two reflections."""
    diff_html = HtmlDiff().make_table(
        original.split(), replayed.split(), fromdesc="original", todesc="replayed"
    )

    anchors = SymbolicMemoryAnchor.objects.all()
    orig_terms: List[str] = []
    new_terms: List[str] = []

    for anchor in anchors:
        if _match_anchor(anchor, original)[0]:
            orig_terms.append(anchor.slug)
        if _match_anchor(anchor, replayed)[0]:
            new_terms.append(anchor.slug)

    changed = sorted(set(orig_terms).symmetric_difference(new_terms))
    intersection = set(orig_terms).intersection(new_terms)
    union = set(orig_terms).union(new_terms)
    anchor_overlap = len(intersection) / float(len(union)) if union else 1.0
    change_score = SequenceMatcher(None, original, replayed).ratio()

    return {
        "diff_html": diff_html,
        "glossary_terms_changed": changed,
        "anchor_overlap": anchor_overlap,
        "change_score": change_score,
    }
