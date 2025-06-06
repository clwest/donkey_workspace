import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from assistants.tests import BaseAPITestCase
from assistants.models import Assistant
from memory.models import SymbolicMemoryAnchor, MemoryEntry
from memory.services.acquisition import update_anchor_acquisition
from assistants.utils.badge_logic import update_assistant_badges


class SetupSummaryAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()

    def test_setup_summary(self):
        assistant = Assistant.objects.create(
            name="Test",
            specialty="demo",
            created_by=self.user,
        )
        anchor = SymbolicMemoryAnchor.objects.create(
            slug="alpha", label="Alpha", description="first", assistant=assistant
        )
        MemoryEntry.objects.create(
            assistant=assistant,
            anchor=anchor,
            event="taught",
            source_user=self.user,
        )
        update_anchor_acquisition(anchor, "acquired")
        update_assistant_badges(assistant, manual={"glossary_apprentice": True})

        url = f"/api/assistants/{assistant.slug}/setup_summary/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["avatar_style"], "robot")
        self.assertEqual(data["tone_profile"], "friendly")
        self.assertEqual(data["initial_glossary_anchor"]["slug"], "alpha")
        self.assertEqual(data["initial_badges"][0]["slug"], "glossary_apprentice")
