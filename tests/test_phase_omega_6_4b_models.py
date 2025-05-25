import pytest

pytest.importorskip("django")

from django.test import Client
from assistants.models import Assistant
from prompts.models import PromptCapsule, CapsuleTransferLog
from agents.models import SwarmAgentRoute, AgentSymbolicMap
from simulation.models import NarrativeMutationTrace


def test_phase_omega_6_4b_models_create(db):
    client = Client()
    a1 = Assistant.objects.create(name="A1", specialty="sage")
    a2 = Assistant.objects.create(name="A2", specialty="scribe")
    capsule = PromptCapsule.objects.create(title="C1", content="x")
    transfer = CapsuleTransferLog.objects.create(capsule=capsule, from_assistant=a1, to_assistant=a2)
    route = SwarmAgentRoute.objects.create(from_assistant=a1, to_assistant=a2, route_type="relay")
    AgentSymbolicMap.objects.create(map_data={})
    trace = NarrativeMutationTrace.objects.create(assistant=a1, mutation_input={"p":1})

    assert transfer.capsule == capsule
    assert route.from_assistant == a1
    assert trace.assistant == a1

    assert client.get("/api/prompts/capsules/").status_code == 200
    assert client.get("/api/swarm/rewire/").status_code == 200
    assert client.get("/api/simulate/narrative/").status_code == 200
