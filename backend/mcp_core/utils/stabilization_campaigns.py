"""Utilities for launching clause stabilization campaigns."""

from agents.models.lore import SwarmMemoryEntry
from metrics.models import CodexClauseVote


def launch_stabilization_campaign(clause_id: str) -> dict:
    """Start a clause stabilization campaign with basic gain/loss metrics."""
    votes = CodexClauseVote.objects.filter(clause_id=clause_id)
    approve = votes.filter(vote_choice__iexact="approve").count()
    reject = votes.filter(vote_choice__iexact="reject").count()
    total = votes.count()

    symbolic_gain = (approve - reject) / float(total or 1)

    entry = SwarmMemoryEntry.objects.create(
        title=f"Stabilization Campaign {clause_id}",
        content=f"approve={approve}, reject={reject}",
        origin="stabilization_campaign",
    )

    return {
        "campaign_id": str(entry.id),
        "clause_id": clause_id,
        "status": "created",
        "proposals": [],
        "voting_open": True,
        "symbolic_gain": symbolic_gain,
    }
