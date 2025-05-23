import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from agents.models import (
    RecursiveRitualContract,
    SwarmMythEngineInstance,
    BeliefFeedbackSignal,
    SwarmCodex,
)


class Phase890ModelTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="A")
        self.codex = SwarmCodex.objects.create(title="C", created_by=self.assistant)

    def test_recursive_ritual_contract(self):
        contract = RecursiveRitualContract.objects.create(
            initiator=self.assistant,
            ritual_cycle_definition={},
            trigger_conditions={},
            symbolic_outputs={},
        )
        self.assertTrue(contract.cycle_active)
        self.assertEqual(contract.initiator, self.assistant)

    def test_swarm_myth_engine_instance(self):
        engine = SwarmMythEngineInstance.objects.create(
            instance_name="E",
            data_inputs={},
            narrative_output="n",
            mythic_tags={},
        )
        self.assertEqual(engine.instance_name, "E")
        self.assertEqual(engine.engine_status, "active")

    def test_belief_feedback_signal(self):
        signal = BeliefFeedbackSignal.objects.create(
            origin_type="user",
            symbolic_impact_vector={},
            target_codex=self.codex,
            myth_response_log="r",
        )
        self.assertEqual(signal.target_codex, self.codex)
        self.assertEqual(signal.origin_type, "user")
