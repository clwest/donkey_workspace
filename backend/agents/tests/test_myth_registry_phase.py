import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from django.test import TestCase
from django.utils import timezone

from assistants.models import Assistant, AssistantGuild, AssistantCivilization
from agents.models import (
    SwarmMemoryEntry,
    LoreToken,
    MythRegistryEntry,
    TemporalLoreAnchor,
    RitualComplianceRecord,
)
from story.models import LoreEntry
from embeddings.models import EMBEDDING_LENGTH


class MythRegistryPhaseTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="A", specialty="logic")
        self.memory = SwarmMemoryEntry.objects.create(title="m", content="c")
        self.token = LoreToken.objects.create(
            name="t",
            summary="s",
            symbolic_tags={},
            embedding=[0.0] * EMBEDDING_LENGTH,
            created_by=self.assistant,
        )
        lore = LoreEntry.objects.create(title="Root", content="x")
        self.guild = AssistantGuild.objects.create(name="G", founding_myth=lore)
        self.civ = AssistantCivilization.objects.create(
            name="Civ", myth_root=lore, symbolic_domain="dream"
        )
        self.civ.founding_guilds.add(self.guild)

    def test_registry_anchor_compliance(self):
        entry = MythRegistryEntry.objects.create(
            memory=self.memory,
            registered_by=self.assistant,
            signature="sig",
            verified_token=self.token,
        )
        self.assertEqual(entry.verified_token, self.token)

        anchor = TemporalLoreAnchor.objects.create(
            anchor_type="solstice",
            timestamp=timezone.now(),
            narrative_impact_summary="impact",
        )
        anchor.attached_tokens.add(self.token)
        anchor.coordinating_civilizations.add(self.civ)

        record = RitualComplianceRecord.objects.create(
            civilization=self.civ, anchor=anchor, compliance_status="fulfilled"
        )
        self.assertEqual(record.compliance_status, "fulfilled")
