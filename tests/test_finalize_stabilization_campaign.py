import pytest

pytest.importorskip("django")

from assistants.models import Assistant
from agents.models.stabilization import (
    StabilizationCampaign,
    CodexClauseVoteLog,
    CodexClauseUpdateLog,
)
from codex.stabilization_logic import finalize_campaign


def test_finalize_campaign(db):
    assistant = Assistant.objects.create(name="A", specialty="seer")
    campaign = StabilizationCampaign.objects.create(
        title="c", target_clause_id="c1", description="orig"
    )
    CodexClauseVoteLog.objects.create(
        campaign=campaign, assistant=assistant, vote_choice="approve"
    )
    result = finalize_campaign(str(campaign.id))
    assert result["updated"] is True
    assert CodexClauseUpdateLog.objects.filter(campaign=campaign).exists()
