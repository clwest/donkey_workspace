import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from agents.models import (
    MythCycleBinding,
    ResurrectionTemplate,
    BeliefContinuityRitual,
    TranscendentMyth,
    SwarmMemoryEntry,
)


class Phase55ModelTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="A")
        self.new_assistant = Assistant.objects.create(name="B")
        self.myth = TranscendentMyth.objects.create(name="Myth")
        self.mem = SwarmMemoryEntry.objects.create(title="t", content="c")

    def test_myth_cycle_binding(self):
        binding = MythCycleBinding.objects.create(
            assistant=self.assistant,
            cycle_name="Legend",
            related_myth=self.myth,
            narrative_role="hero",
            cycle_phase="origin",
        )
        self.assertEqual(binding.assistant, self.assistant)
        self.assertEqual(binding.related_myth, self.myth)

    def test_resurrection_template(self):
        template = ResurrectionTemplate.objects.create(
            title="Return",
            base_traits={"courage": 1},
            symbolic_tags={"phase": "rebirth"},
            recommended_archetype="sage",
            created_by=self.assistant,
        )
        template.seed_memories.add(self.mem)
        self.assertEqual(template.seed_memories.count(), 1)

    def test_belief_continuity_ritual(self):
        ritual = BeliefContinuityRitual.objects.create(
            outgoing_assistant=self.assistant,
            incoming_assistant=self.new_assistant,
            values_transferred={"virtue": "honor"},
            ritual_type="echo",
        )
        ritual.memory_reference.add(self.mem)
        self.assertEqual(ritual.memory_reference.count(), 1)
