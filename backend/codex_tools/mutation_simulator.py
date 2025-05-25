"""Simple codex mutation simulator."""

from typing import List, Dict


def mutate_codex_clauses(clauses: List[str], mutations: Dict[str, str]) -> List[str]:
    """Return mutated clauses applying string replacements."""
    mutated = []
    for clause in clauses:
        text = clause
        for target, replacement in mutations.items():
            text = text.replace(target, replacement)
        mutated.append(text)
    return mutated


def summarize_mutation(original: List[str], mutated: List[str]) -> Dict[str, int]:
    """Return basic stats about the codex mutation."""
    changed = sum(1 for o, m in zip(original, mutated) if o != m)
    return {"total": len(original), "changed": changed}
