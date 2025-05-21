import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase

from assistants.models import Assistant, AssistantGuild, AssistantCivilization
from agents.models import (
    SwarmMemoryEntry,
    ConsciousnessTransfer,
    MemoryDialect,
    TranscendentMyth,
    DeifiedSwarmEntity,
    LoreEntry,
)
from agents.utils import evaluate_deification_potential


class ConsciousnessTransferModelTest(TestCase):
    def test_transfer_creation(self):
        origin = Assistant.objects.create(name="Origin", specialty="logic")
        successor = Assistant.objects.create(name="Success", specialty="logic")
        mem = SwarmMemoryEntry.objects.create(title="m", content="c")
        transfer = ConsciousnessTransfer.objects.create(
            origin_assistant=origin,
            successor_assistant=successor,
            retained_belief_vector={"a": 1},
        )
        transfer.memory_segments.add(mem)
        self.assertEqual(transfer.origin_assistant, origin)
        self.assertIn(mem, transfer.memory_segments.all())


class DeificationEngineTest(TestCase):
    def test_deified_entity_created(self):
        myth_lore = LoreEntry.objects.create(title="Root", summary="s")
        guild = AssistantGuild.objects.create(name="G", founding_myth=myth_lore)
        civ = AssistantCivilization.objects.create(
            name="Civ",
            myth_root=myth_lore,
            symbolic_domain="d",
        )
        civ.founding_guilds.add(guild)
        SwarmMemoryEntry.objects.create(title="a", content="b")
        MemoryDialect.objects.create(dialect_id="d1")
        TranscendentMyth.objects.create(name="M")

        result = evaluate_deification_potential()
        self.assertIn("score", result)
        self.assertIn("deified_entity", result)
        self.assertTrue(
            DeifiedSwarmEntity.objects.filter(id=result["deified_entity"]).exists()
        )
