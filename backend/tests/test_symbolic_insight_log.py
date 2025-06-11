import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.test_settings")
import django

django.setup()

from django.test import TestCase
from rest_framework.test import APIClient
from assistants.models import Assistant
from agents.models import Agent
from intel_core.models import Document
from memory.models import MemoryEntry, SymbolicMemoryAnchor
from insights.models import SymbolicAgentInsightLog
from insights.services import detect_document_conflicts


class SymbolicInsightLogTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.assistant = Assistant.objects.create(name="A")
        self.agent = Agent.objects.create(name="agent", slug="a1", parent_assistant=self.assistant)
        self.anchor = SymbolicMemoryAnchor.objects.create(
            slug="fact",
            label="Fact",
            assistant=self.assistant,
            memory_context=self.assistant.memory_context,
        )
        self.memory = MemoryEntry.objects.create(
            assistant=self.assistant,
            summary="Important fact",
            event="Important fact",
            anchor=self.anchor,
        )
        self.document = Document.objects.create(
            title="Doc",
            content="This contradicts the important fact",
            source_type="text",
        )

    def test_conflict_logged_and_endpoint(self):
        detect_document_conflicts(self.assistant, self.document)
        self.assertEqual(SymbolicAgentInsightLog.objects.count(), 1)
        resp = self.client.get("/api/insights/conflict_logs/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["results"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["symbol"], "fact")
