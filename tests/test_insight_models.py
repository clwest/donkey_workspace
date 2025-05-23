import pytest
pytest.importorskip("django")

from assistants.models import Assistant
from agents.models import InsightHub, PerspectiveMergeEvent, TimelineStitchLog, LoreToken, SwarmMemoryEntry


def test_insight_models_create(db):
    assistant = Assistant.objects.create(name="A", specialty="test")
    token = LoreToken.objects.create(name="T", summary="s", created_by=assistant)
    mem = SwarmMemoryEntry.objects.create(title="m", content="c")

    hub = InsightHub.objects.create(name="H", focus_topics={"a": 1})
    hub.publishing_assistants.add(assistant)
    hub.active_tokens.add(token)
    hub.memory_feed.add(mem)

    merge = PerspectiveMergeEvent.objects.create(
        topic="merge", resolution_summary="r", merged_insight="m"
    )
    merge.assistants_involved.add(assistant)
    merge.contrasting_memories.add(mem)

    stitch = TimelineStitchLog.objects.create(
        initiated_by=assistant,
        stitching_method="echo",
        unified_thread_summary="u",
    )
    stitch.narrative_fragments.add(mem)

    assert hub.publishing_assistants.count() == 1
    assert merge.assistants_involved.count() == 1
    assert stitch.narrative_fragments.count() == 1
