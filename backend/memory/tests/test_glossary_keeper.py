import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.test_settings")
import django

django.setup()

from django.test import TestCase
from unittest.mock import patch
from django.utils import timezone
from datetime import timedelta

from assistants.models import Assistant
from memory.models import (
    SymbolicMemoryAnchor,
    RAGGroundingLog,
    AnchorReinforcementLog,
    GlossaryKeeperLog,
    MemoryEntry,
)
from memory.glossary_keeper import run_keeper_tasks


class GlossaryKeeperTests(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="A", slug="claritybot")
        self.anchor = SymbolicMemoryAnchor.objects.create(
            slug="term", label="Term", assistant=self.assistant, memory_context=self.assistant.memory_context
        )

    @patch("memory.glossary_keeper.call_gpt4", return_value="Better")
    def test_fallback_triggers_mutation(self, mock_call):
        for _ in range(8):
            RAGGroundingLog.objects.create(
                assistant=self.assistant,
                query="q",
                used_chunk_ids=["1"],
                fallback_triggered=True,
                glossary_hits=[],
                glossary_misses=[self.anchor.slug],
                retrieval_score=0.0,
                expected_anchor=self.anchor.slug,
                adjusted_score=0.0,
            )
        run_keeper_tasks(self.assistant)
        self.anchor.refresh_from_db()
        self.assertEqual(self.anchor.suggested_label, "Better")
        self.assertEqual(GlossaryKeeperLog.objects.filter(anchor=self.anchor).count(), 2)
        self.assertTrue(MemoryEntry.objects.filter(anchor=self.anchor, tags__slug="glossary_drift").exists())
        mock_call.assert_called()

    @patch("memory.glossary_keeper.call_gpt4", return_value="Better")
    def test_stale_reinforcement_creates_reflection(self, mock_call):
        log = AnchorReinforcementLog.objects.create(anchor=self.anchor, assistant=self.assistant, reason="t")
        log.created_at = timezone.now() - timedelta(days=40)
        log.save(update_fields=["created_at"])
        self.anchor.avg_score = 0.1
        self.anchor.save(update_fields=["avg_score"])
        run_keeper_tasks(self.assistant)
        self.assertTrue(MemoryEntry.objects.filter(anchor=self.anchor, tags__slug="glossary_drift").exists())
        self.assertEqual(GlossaryKeeperLog.objects.filter(action_taken="reflection_written").count(), 1)
        mock_call.assert_called()

