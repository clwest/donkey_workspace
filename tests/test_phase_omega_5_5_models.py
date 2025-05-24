import pytest

pytest.importorskip("django")

from assistants.models import Assistant
from simulation.models import (
    SwarmReflectionThread,
    SwarmReflectionPlaybackLog,
    PromptCascadeLog,
    CascadeNodeLink,
    SimulationClusterStatus,
    SimulationGridNode,
)


def test_phase_omega_5_5_models_create(db):
    assistant = Assistant.objects.create(name="A")

    thread = SwarmReflectionThread.objects.create(title="T")
    playback = SwarmReflectionPlaybackLog.objects.create(
        thread=thread,
        assistant=assistant,
        timeline=[{"t": 1}],
    )

    cascade = PromptCascadeLog.objects.create(
        prompt_id="p1",
        triggered_by=assistant,
        cascade_path=[{"step": 1}],
    )
    CascadeNodeLink.objects.create(cascade=cascade, assistant=assistant)

    cluster = SimulationClusterStatus.objects.create(
        cluster_name="C",
        phase="init",
        entropy_level=0.1,
    )
    node = SimulationGridNode.objects.create(cluster=cluster, assistant=assistant)

    assert playback.thread == thread
    assert cascade.triggered_by == assistant
    assert node.cluster == cluster
