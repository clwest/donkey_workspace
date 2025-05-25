from __future__ import annotations

from typing import Tuple

from agents.models.lore import SwarmMemoryEntry
from metrics.models import CodexClauseVote


def launch_stabilization_campaign(clause_id: str) -> str:
    """Create a stabilization campaign for a codex clause.

    The function aggregates existing votes for the given ``clause_id`` and
    records a summary ``SwarmMemoryEntry``. A simple symbolic gain/loss is
    estimated from approve vs. reject vote counts.

    Returns the ID of the created memory entry as a string.
    """

    votes = CodexClauseVote.objects.filter(clause_id=clause_id)
    approve = votes.filter(vote_choice__iexact="approve").count()
    reject = votes.filter(vote_choice__iexact="reject").count()
    total = votes.count()

    gain_score = (approve - reject) / float(total or 1)
    loss_score = (reject - approve) / float(total or 1)

    summary = (
        f"Clause {clause_id} stabilization:\n"
        f"approve={approve}, reject={reject}, total={total}, "
        f"gain={gain_score:.2f}, loss={loss_score:.2f}"
    )

    entry = SwarmMemoryEntry.objects.create(
        title=f"Stabilization Campaign {clause_id}",
        content=summary,
        origin="stabilization_campaign",
    )

    return str(entry.id)
