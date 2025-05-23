import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from agents.models import (
    EncodedRitualBlueprint,
    RitualSimulationLog,
    MemoryReprogrammingScript,
    SwarmMemoryEntry,
)


class Phase68ModelTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="A")
        self.memory = SwarmMemoryEntry.objects.create(title="M", content="c")

    def test_encoded_ritual_blueprint(self):
        bp = EncodedRitualBlueprint.objects.create(
            name="R",
            creator=self.assistant,
            symbolic_steps={},
            transformation_goal="g",
            applicable_roles=["sage"],
        )
        self.assertEqual(bp.creator, self.assistant)

    def test_ritual_simulation_log(self):
        bp = EncodedRitualBlueprint.objects.create(
            name="R2",
            creator=self.assistant,
            symbolic_steps={},
            transformation_goal="g",
            applicable_roles=[],
        )
        log = RitualSimulationLog.objects.create(
            assistant=self.assistant,
            blueprint=bp,
            outcome_description="ok",
            symbolic_success_rate=0.8,
        )
        self.assertEqual(log.blueprint, bp)

    def test_memory_reprogramming_script(self):
        script = MemoryReprogrammingScript.objects.create(
            target_memory=self.memory,
            initiated_by=self.assistant,
            trigger_condition="dream",
            rewrite_directive="revise",
        )
        self.assertEqual(script.validation_result, "pending")
