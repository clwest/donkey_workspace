"""Utilities for launching clause stabilization campaigns."""

from django.apps import apps
from agents.models.lore import SwarmMemoryEntry
from metrics.models import CodexClauseVote
from agents.models.stabilization import (
    StabilizationCampaign,
    CampaignSymbolicGainEstimate,
)


def launch_stabilization_campaign(clause_id: str) -> dict:
    """Start a clause stabilization campaign with basic gain/loss metrics."""
    Clause = apps.get_model("agents", "CodexClause")
    if not Clause.objects.filter(id=clause_id).exists():
        raise ValueError("Clause not found")

    votes = CodexClauseVote.objects.filter(clause_id=clause_id)
    approve = votes.filter(vote_choice__iexact="approve").count()
    reject = votes.filter(vote_choice__iexact="reject").count()
    total = votes.count()

    symbolic_gain = (approve - reject) / float(total or 1)

    campaign = StabilizationCampaign.objects.create(
        title=f"Stabilization {clause_id}",
        target_clause_id=str(clause_id),
    )

    CampaignSymbolicGainEstimate.objects.create(
        campaign=campaign, estimated_gain=symbolic_gain
    )

    SwarmMemoryEntry.objects.create(
        title=f"Stabilization Campaign {clause_id}",
        content=f"approve={approve}, reject={reject}",
        origin="stabilization_campaign",
    )

    return {
        "campaign_id": str(campaign.id),
        "clause_id": str(clause_id),
        "status": campaign.status,
        "proposals": [],
        "voting_open": True,
        "symbolic_gain": symbolic_gain,
    }
