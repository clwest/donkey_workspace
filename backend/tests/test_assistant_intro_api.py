import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from assistants.tests import BaseAPITestCase
from assistants.models import Assistant


class AssistantIntroAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()

    def test_intro_endpoint(self):
        assistant = Assistant.objects.create(
            name="IntroBot",
            specialty="demo",
            intro_text="Hello there!",
            archetype="Helper",
            created_by=self.user,
        )
        url = f"/api/assistants/{assistant.slug}/intro/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["name"], "IntroBot")
        self.assertEqual(data["archetype"], "Helper")
        self.assertEqual(data["intro_text"], "Hello there!")
        self.assertIn("trail_summary_ready", data)
