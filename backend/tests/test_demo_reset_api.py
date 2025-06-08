import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from assistants.tests import BaseAPITestCase
from assistants.models import Assistant
from memory.models import MemoryEntry


class DemoResetAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        self.demo = Assistant.objects.create(name="Demo", slug="demo", is_demo=True)
        self.normal = Assistant.objects.create(name="Real", slug="real")
        MemoryEntry.objects.create(assistant=self.demo, event="hello")
        MemoryEntry.objects.create(assistant=self.normal, event="hi")

    def test_only_demo_allowed(self):
        url = f"/api/assistants/{self.normal.slug}/reset_demo/"
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 404)

    def test_demo_memories_reset(self):
        old_ids = list(self.demo.memories.values_list("id", flat=True))
        from assistants.models.reflection import AssistantReflectionLog
        AssistantReflectionLog.objects.create(
            assistant=self.demo, title="t", summary="s"
        )
        url = f"/api/assistants/{self.demo.slug}/reset_demo/"
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)
        new_ids = list(self.demo.memories.values_list("id", flat=True))
        self.assertTrue(len(new_ids) > 0)
        self.assertTrue(set(old_ids).isdisjoint(set(new_ids)))
        self.assertEqual(AssistantReflectionLog.objects.filter(assistant=self.demo).count(), 0)

    def test_force_seed_param(self):
        self.demo.delete()
        url = f"/api/assistants/{'demo'}/reset_demo/?force_seed=true"
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)

