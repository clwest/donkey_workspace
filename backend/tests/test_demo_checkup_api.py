import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from assistants.tests import BaseAPITestCase
from assistants.models import Assistant
from prompts.models import Prompt
from mcp_core.models import MemoryContext
from memory.models import MemoryEntry
from assistants.models.reflection import AssistantReflectionLog


class DemoCheckupAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        prompt = Prompt.objects.create(title="p", content="You are helpful.")
        ctx = MemoryContext.objects.create(content="ctx")
        self.demo1 = Assistant.objects.create(
            name="Demo1", slug="demo1", is_demo=True, system_prompt=prompt, memory_context=ctx
        )
        self.demo2 = Assistant.objects.create(
            name="Demo2", slug="demo2", is_demo=True, memory_context=ctx
        )
        self.demo3 = Assistant.objects.create(
            name="Demo3", slug="demo3", is_demo=True, system_prompt=prompt, memory_context=ctx
        )
        MemoryEntry.objects.create(assistant=self.demo1, event="e1", context=ctx, is_demo=True)
        MemoryEntry.objects.create(assistant=self.demo1, event="e2", context=ctx)
        AssistantReflectionLog.objects.create(assistant=self.demo1, title="t", summary="s")
        self.url = "/api/assistants/demo_checkup/"

    def test_demo_checkup(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertGreaterEqual(len(data), 3)
        entry = next(d for d in data if d["slug"] == "demo1")
        self.assertTrue(entry["has_system_prompt"])
        self.assertTrue(entry["has_memory_context"])
        self.assertEqual(entry["memory_count"], 2)
        self.assertEqual(entry["starter_chat_count"], 1)
        self.assertEqual(entry["reflection_count"], 1)
        entry2 = next(d for d in data if d["slug"] == "demo2")
        self.assertFalse(entry2["has_system_prompt"])
