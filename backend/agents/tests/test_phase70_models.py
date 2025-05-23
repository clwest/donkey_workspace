import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant, AssistantGuild
from agents.models import (
    SwarmCosmology,
    LivingBeliefEngine,
    TemporalPurposeArchive,
    SwarmCodex,
    SwarmMemoryEntry,
)
from agents.models.cosmology import update_belief_state


class Phase70ModelsTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="Alpha")
        self.guild = AssistantGuild.objects.create(name="Guild")
        self.codex = SwarmCodex.objects.create(
            title="Codex", created_by=self.assistant, symbolic_domain="order"
        )
        self.memory = SwarmMemoryEntry.objects.create(title="m", content="c")

    def test_swarm_cosmology_creation(self):
        cos = SwarmCosmology.objects.create(name="Cosmo")
        cos.symbolic_laws.add(self.codex)
        cos.founding_guilds.add(self.guild)
        self.assertEqual(cos.symbolic_laws.count(), 1)
        self.assertEqual(cos.founding_guilds.count(), 1)

    def test_belief_engine_update(self):
        engine = LivingBeliefEngine.objects.create(assistant=self.assistant)
        engine.influence_sources.add(self.memory)
        update_belief_state(self.assistant.id)
        engine.refresh_from_db()
        self.assertIn("influence_count", engine.current_alignment)
        self.assertGreater(engine.belief_entropy, 0)

    def test_purpose_archive_creation(self):
        arc = TemporalPurposeArchive.objects.create(
            assistant=self.assistant,
            purpose_history=[{"t": "start", "p": "assist"}],
            symbolic_tags={"phase": "testing"},
        )
        self.assertEqual(arc.purpose_history[0]["p"], "assist")
