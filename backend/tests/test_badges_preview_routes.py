import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from django.core.management import call_command
from assistants.tests import BaseAPITestCase
from assistants.models import Assistant
from memory.models import MemoryEntry
from assistants.models.reflection import AssistantReflectionLog


class BadgePreviewRoutesTest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        call_command("seed_demo_assistants")
        self.assistant = Assistant.objects.get(slug="prompt-pal")
        MemoryEntry.objects.create(
            assistant=self.assistant,
            event="hi",
            full_transcript="hello",
        )
        AssistantReflectionLog.objects.create(
            assistant=self.assistant,
            title="t",
            summary="reflect",
        )

    def test_badge_list_filters_by_assistant(self):
        resp = self.client.get("/api/badges/?assistant=prompt-pal")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        badges = data.get("badges") or data
        self.assertGreaterEqual(len(badges), 1)

    def test_preview_route(self):
        url = f"/api/assistants/{self.assistant.slug}/preview/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["slug"], self.assistant.slug)
        self.assertEqual(data["memory_count"], 1)
        self.assertTrue(data["latest_reflection"].startswith("reflect"))
