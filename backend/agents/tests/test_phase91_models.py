import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from agents.models import (
    NarrativeTrainingGround,
    SwarmMythEditLog,
    LegacyContinuityVault,
    TranscendentMyth,
    SwarmCodex,
    SwarmMemoryEntry,
)


class Phase91ModelTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="A")
        self.myth = TranscendentMyth.objects.create(name="M")
        self.codex = SwarmCodex.objects.create(title="C", created_by=self.assistant)
        self.mem = SwarmMemoryEntry.objects.create(title="t", content="c")

    def test_training_ground(self):
        ground = NarrativeTrainingGround.objects.create(
            training_title="T",
            scenario_description="s",
            target_archetypes={},
        )
        ground.involved_assistants.add(self.assistant)
        ground.memory_feed.add(self.mem)
        self.assertEqual(ground.involved_assistants.count(), 1)
        self.assertEqual(ground.memory_feed.count(), 1)

    def test_myth_edit_log(self):
        log = SwarmMythEditLog.objects.create(
            edit_summary="e",
            affected_myth=self.myth,
            before_state="b",
            after_state="a",
        )
        log.editor_assistants.add(self.assistant)
        self.assertEqual(log.editor_assistants.count(), 1)
        self.assertFalse(log.approved)

    def test_legacy_continuity_vault(self):
        vault = LegacyContinuityVault.objects.create(
            vault_name="V",
            preserved_archetypes={},
            narrative_epoch="ep",
        )
        vault.assistant_snapshots.add(self.assistant)
        vault.codex_archives.add(self.codex)
        self.assertEqual(vault.codex_archives.count(), 1)
        self.assertEqual(vault.assistant_snapshots.count(), 1)
