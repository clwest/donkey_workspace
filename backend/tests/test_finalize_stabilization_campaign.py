import pytest

pytest.importorskip("django")

from assistants.models import Assistant
from agents.models.stabilization import (
    StabilizationCampaign,
    CodexClauseVoteLog,
    CodexClauseUpdateLog,
)
from codex.stabilization_logic import finalize_campaign
from memory.models import MemoryEntry

from unittest.mock import patch


@patch("assistants.utils.reflection_engine.call_llm")
def test_finalize_campaign(mock_call, db):
    mock_call.return_value = "- shift"
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
    log = CodexClauseUpdateLog.objects.get(campaign=campaign)
    assert result["clause_before"] == "orig"
    assert result["clause_after"] == log.clause_after
    mem = MemoryEntry.objects.filter(assistant=assistant, related_campaign=campaign).first()
    assert mem is not None and mem.symbolic_change is True
