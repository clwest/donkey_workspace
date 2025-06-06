import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from assistants.tests import BaseAPITestCase
from assistants.models import AssistantHintState, Assistant


class AssistantHintsAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        self.assistant = Assistant.objects.create(name="A", slug="a")

    def test_hint_dismiss_flow(self):
        url = f"/api/assistants/{self.assistant.slug}/hints/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["hints"]
        self.assertEqual(len(data), 2)
        self.assertFalse(any(h["dismissed"] for h in data))

        dismiss_url = f"/api/assistants/{self.assistant.slug}/hints/rag_intro/dismiss/"
        resp = self.client.post(dismiss_url)
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["hints"]
        dismissed = next(h for h in data if h["id"] == "rag_intro")
        self.assertTrue(dismissed["dismissed"])
