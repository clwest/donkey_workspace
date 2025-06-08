import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from assistants.tests import BaseAPITestCase
from assistants.models import Assistant
from memory.models import SymbolicMemoryAnchor, MemoryEntry


class DefaultTemplateAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        self.user.assistant_name = "Helper"
        self.user.assistant_personality = "cheerful"
        self.user.goals = "assist with tasks"
        self.user.save()
        self.demo = Assistant.objects.create(name="Demo", slug="demo", demo_slug="demo", is_demo=True)
        self.clone = Assistant.objects.create(
            name="Clone",
            slug="clone",
            created_by=self.user,
            is_demo_clone=True,
            spawned_by=self.demo,
        )
        self.anchor = SymbolicMemoryAnchor.objects.create(
            slug="alpha",
            label="Alpha",
            description="first",
            assistant=self.clone,
        )
        MemoryEntry.objects.create(
            assistant=self.clone,
            anchor=self.anchor,
            source_user=self.user,
            event="taught",
        )

    def test_default_template(self):
        resp = self.client.get("/api/assistants/default_template/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["name"], "Helper")
        self.assertEqual(data["personality"], "cheerful")
        self.assertIsNotNone(data["mentor"])
        self.assertEqual(data["mentor"]["demo_slug"], "demo")
        slugs = [t["slug"] for t in data["starter_terms"]]
        self.assertIn("alpha", slugs)

