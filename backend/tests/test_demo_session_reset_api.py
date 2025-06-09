import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from assistants.tests import BaseAPITestCase
from assistants.models import Assistant
from assistants.models.demo_usage import DemoSessionLog
from assistants.models.demo import DemoUsageLog
from assistants.models.trail import TrailMarkerLog


class DemoSessionResetAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        self.demo = Assistant.objects.create(name="Demo", slug="demo", is_demo=True)
        DemoSessionLog.objects.create(assistant=self.demo, session_id="s1")

    def test_basic_reset(self):
        DemoUsageLog.objects.create(session_id="s1", demo_slug="demo")
        url = "/api/assistants/demo_session/reset/"
        resp = self.client.post(url, {"session_id": "s1"}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(DemoSessionLog.objects.filter(session_id="s1").exists())
        self.assertTrue(DemoUsageLog.objects.filter(session_id="s1").exists())

    def test_full_reset_and_marker(self):
        DemoUsageLog.objects.create(session_id="s1", demo_slug="demo")
        url = "/api/assistants/demo_session/reset/?full_reset=true"
        resp = self.client.post(url, {"session_id": "s1"}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(DemoSessionLog.objects.filter(session_id="s1").exists())
        self.assertFalse(DemoUsageLog.objects.filter(session_id="s1").exists())
        self.assertTrue(
            TrailMarkerLog.objects.filter(
                assistant=self.demo, marker_type="demo_session_reset"
            ).exists()
        )
