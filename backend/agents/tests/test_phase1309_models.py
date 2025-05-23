import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant, CodexLinkedGuild
from agents.models import (
    SwarmMemoryEntry,
    SwarmCodex,
    MythchainOutputGenerator,
    NarrativeArtifactExporter,
    SymbolicPatternBroadcastEngine,
)

class Phase1309ModelsTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="A")
        self.memory = SwarmMemoryEntry.objects.create(title="m", content="c")
        self.codex = SwarmCodex.objects.create(title="C", created_by=self.assistant, symbolic_domain="myth")
        self.guild = CodexLinkedGuild.objects.create(guild_name="g", codex=self.codex)

    def test_models_create(self):
        gen = MythchainOutputGenerator.objects.create(
            assistant=self.assistant,
            output_title="O",
            codex_alignment_map={},
            symbolic_summary="s",
        )
        gen.seed_memory.add(self.memory)

        export = NarrativeArtifactExporter.objects.create(
            assistant=self.assistant,
            artifact_title="A",
            export_format="json",
        )

        engine = SymbolicPatternBroadcastEngine.objects.create(
            broadcast_title="B",
            source_guild=self.guild,
            symbolic_payload={},
            belief_waveform_data={},
        )
        engine.target_assistants.add(self.assistant)

        self.assertEqual(gen.seed_memory.count(), 1)
        self.assertEqual(export.assistant, self.assistant)
        self.assertEqual(engine.target_assistants.count(), 1)
