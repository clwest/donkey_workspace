import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from assistants.tests import BaseAPITestCase
from assistants.models import Assistant
from assistants.models.demo_usage import DemoSessionLog
from assistants.models.demo import DemoUsageLog
from assistants.models.reflection import AssistantReflectionLog
from memory.models import SymbolicMemoryAnchor, AnchorReinforcementLog, MemoryEntry
from mcp_core.models import Tag

class DemoOverlayAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        self.assistant = Assistant.objects.create(name="Demo", slug="demo", is_demo=True, demo_slug="demo")
        self.session_id = "11111111-1111-1111-1111-111111111111"
        DemoSessionLog.objects.create(assistant=self.assistant, session_id=self.session_id)
        anchor = SymbolicMemoryAnchor.objects.create(label="Test", slug="test", memory_context=self.assistant.memory_context)
        AnchorReinforcementLog.objects.create(anchor=anchor, assistant=self.assistant)
        mem = MemoryEntry.objects.create(assistant=self.assistant, session_id=self.session_id, event="e")
        tag, _ = Tag.objects.get_or_create(slug="t1", defaults={"name":"t1"})
        mem.tags.add(tag)
        self.reflection = AssistantReflectionLog.objects.create(assistant=self.assistant, title="Demo", summary="hello", demo_reflection=True)
        DemoUsageLog.objects.create(session_id=self.session_id, demo_slug="demo", reflection=self.reflection)

    def test_overlay(self):
        url = f"/api/assistants/{self.assistant.slug}/demo_overlay/?session_id={self.session_id}"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("anchors", data)
        self.assertIn("tags", data)
        self.assertEqual(data["reflection_snippet"], "hello")
