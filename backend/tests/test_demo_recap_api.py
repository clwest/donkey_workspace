import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from assistants.tests import BaseAPITestCase
from assistants.models import Assistant
from assistants.models.demo_usage import DemoSessionLog
from assistants.models.demo import DemoUsageLog


class DemoRecapAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        self.assistant = Assistant.objects.create(
            name="Demo", slug="demo", demo_slug="demo", is_demo=True
        )
        self.session_id = "11111111-1111-1111-1111-111111111111"
        DemoSessionLog.objects.create(
            assistant=self.assistant, session_id=self.session_id, message_count=4
        )

    def test_hide_after_shown(self):
        url = f"/api/assistants/demo_recap/{self.session_id}/"
        with self.assertLogs("assistants.views.demo", level="DEBUG") as logs:
            resp1 = self.client.get(url)
        self.assertEqual(resp1.status_code, 200)
        data = resp1.json()
        self.assertIn("messages_sent", data)
        self.assertTrue(
            DemoUsageLog.objects.get(session_id=self.session_id).recap_shown
        )
        self.assertFalse(
            any("Missing session or usage" in m for m in logs.output)
        )
        resp2 = self.client.get(url)
        self.assertEqual(resp2.status_code, 404)

    def test_missing_session_returns_empty(self):
        bad = "22222222-2222-2222-2222-222222222222"
        resp = self.client.get(f"/api/assistants/demo_recap/{bad}/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), {})

    def test_force_usage_param(self):
        DemoUsageLog.objects.filter(session_id=self.session_id).delete()
        url = (
            f"/api/assistants/demo_recap/{self.session_id}/?force_usage=1"
        )
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(
            DemoUsageLog.objects.filter(session_id=self.session_id).exists()
        )
