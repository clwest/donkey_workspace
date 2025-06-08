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
        DemoSessionLog.objects.create(
            assistant=self.assistant, session_id="s1", message_count=4
        )

    def test_hide_after_shown(self):
        url = "/api/assistants/demo_recap/s1/"
        resp1 = self.client.get(url)
        self.assertEqual(resp1.status_code, 200)
        self.assertTrue(DemoUsageLog.objects.get(session_id="s1").recap_shown)
        resp2 = self.client.get(url)
        self.assertEqual(resp2.status_code, 404)
