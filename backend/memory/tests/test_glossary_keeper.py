import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from unittest.mock import patch
from django.test import TestCase
from assistants.models import Assistant
from memory.models import SymbolicMemoryAnchor, GlossaryKeeperLog, MemoryEntry
from memory.utils.glossary_keeper import run_keeper_tasks


class GlossaryKeeperTests(TestCase):
    @patch("memory.utils.glossary_keeper.call_gpt4", return_value="Better\nreason")
    @patch("memory.utils.glossary_keeper.calculate_anchor_drift", return_value=0.8)
    def test_keeper_updates_anchor(self, mock_drift, mock_call):
        assistant = Assistant.objects.create(name="C", slug="claritybot")
        anchor = SymbolicMemoryAnchor.objects.create(slug="zk", label="ZK", assistant=assistant)
        run_keeper_tasks(assistant=assistant)
        anchor.refresh_from_db()
        self.assertEqual(anchor.suggested_label, "Better")
        self.assertTrue(MemoryEntry.objects.filter(anchor=anchor, tags__slug="glossary_drift").exists())
        self.assertEqual(GlossaryKeeperLog.objects.count(), 1)
        log = GlossaryKeeperLog.objects.first()
        self.assertEqual(log.action_taken, "suggested_mutation")
        mock_call.assert_called_once()
