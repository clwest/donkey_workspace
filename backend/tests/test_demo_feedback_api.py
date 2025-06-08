import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from assistants.tests import BaseAPITestCase
from assistants.models import Assistant
from assistants.models.demo import DemoUsageLog
from assistants.models.demo_usage import DemoSessionLog
from django.utils import timezone


class DemoFeedbackAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        self.assistant = Assistant.objects.create(
            name="Demo", slug="demo", is_demo=True
        )
        self.session = DemoSessionLog.objects.create(
            assistant=self.assistant,
            session_id="s1",
            message_count=3,
            starter_query="hello",
            demo_interaction_score=6,
            converted_to_real_assistant=True,
            tips_helpful=2,
        )
        self.usage = DemoUsageLog.objects.create(
            session_id="s1",
            demo_slug="demo",
            feedback_text="great",
            user_rating=5,
            converted_at=timezone.now(),
        )

    def test_list_feedback(self):
        resp = self.client.get("/api/assistants/demo_feedback/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["results"][0]
        self.assertEqual(data["session_id"], "s1")
        self.assertEqual(data["rating"], 5)
        self.assertEqual(data["message_count"], 3)

    def test_filters(self):
        DemoSessionLog.objects.create(assistant=self.assistant, session_id="s2")
        DemoUsageLog.objects.create(session_id="s2", demo_slug="demo", user_rating=3)
        url = "/api/assistants/demo_feedback/?rating=5&converted=true&demo_slug=demo"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()["results"]), 1)
        self.assertEqual(resp.json()["results"][0]["session_id"], "s1")
