from __future__ import annotations

from typing import Dict

from django.apps import apps
from assistants.utils.reflection_engine import log_symbolic_reflection


def finalize_campaign(campaign_id: str) -> Dict:
    """Finalize a stabilization campaign based on recorded votes."""
    StabilizationCampaign = apps.get_model("agents", "StabilizationCampaign")
    CodexClauseVoteLog = apps.get_model("agents", "CodexClauseVoteLog")
    CodexClauseUpdateLog = apps.get_model("agents", "CodexClauseUpdateLog")
    SwarmMemoryEntry = apps.get_model("agents", "SwarmMemoryEntry")
    Tag = apps.get_model("mcp_core", "Tag")
    Assistant = apps.get_model("assistants", "Assistant")

    campaign = StabilizationCampaign.objects.filter(id=campaign_id).first()
    if not campaign:
        raise ValueError(f"Campaign {campaign_id} not found")

    votes = CodexClauseVoteLog.objects.filter(campaign=campaign)
    approve = votes.filter(vote_choice__iexact="approve").count()
    reject = votes.filter(vote_choice__iexact="reject").count()
    total = votes.count()
    gain = (approve - reject) / float(total or 1)

    clause_before = campaign.description or ""
    clause_after = clause_before
    changed = False
    if approve > reject:
        clause_after = clause_before + "\n[UPDATED]"
        changed = True

    update_log = CodexClauseUpdateLog.objects.create(
        campaign=campaign,
        clause_before=clause_before,
        clause_after=clause_after,
        symbolic_gain=max(gain, 0.0),
        symbolic_loss=max(-gain, 0.0),
    )

    campaign.status = "closed"
    campaign.save(update_fields=["status"])

    tag, _ = Tag.objects.get_or_create(
        slug="symbolic_change", defaults={"name": "symbolic_change"}
    )
    assistant_ids = list(votes.values_list("assistant", flat=True).distinct())
    if changed:
        entry = SwarmMemoryEntry.objects.create(
            title=f"Codex clause {campaign.target_clause_id} updated",
            content=f"gain={gain:.2f}",
            origin="stabilization_finalize",
        )
        entry.tags.add(tag)
        for assistant_id in assistant_ids:
            entry.linked_agents.add(assistant_id)

    for assistant in Assistant.objects.filter(id__in=assistant_ids):
        log_symbolic_reflection(
            assistant=assistant,
            clause_before=clause_before,
            clause_after=clause_after,
            symbolic_gain=gain,
            campaign_id=campaign.id,
        )

    return {
        "campaign_id": campaign_id,
        "approve": approve,
        "reject": reject,
        "symbolic_gain": gain,
        "updated": changed,
        "update_log": update_log.id,
        "clause_before": clause_before,
        "clause_after": clause_after,
    }
