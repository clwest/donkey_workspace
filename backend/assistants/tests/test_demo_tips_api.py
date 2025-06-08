import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from assistants.tests import BaseAPITestCase
from assistants.models import Assistant
from assistants.demo_config import DEMO_TIPS


class DemoTipsAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        self.demo = Assistant.objects.create(name="Demo", slug="demo", is_demo=True)
        self.normal = Assistant.objects.create(name="Normal", slug="normal")

    def test_demo_tips_returned_for_demo(self):
        url = f"/api/assistants/{self.demo.slug}/demo_tips/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["tips"], DEMO_TIPS)

    def test_non_demo_returns_empty(self):
        url = f"/api/assistants/{self.normal.slug}/demo_tips/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["tips"], [])
