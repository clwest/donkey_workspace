import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from assistants.tests import BaseAPITestCase
from assistants.models import AssistantHintState, Assistant
from assistants.hint_config import HINTS


class AssistantHintsAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        self.assistant = Assistant.objects.create(name="A", slug="a")

    def test_hint_dismiss_flow(self):
        url = f"/api/assistants/{self.assistant.slug}/hints/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["hints"]
        self.assertEqual(len(data), len(HINTS))
        self.assertFalse(any(h["dismissed"] for h in data))

        dismiss_url = f"/api/assistants/{self.assistant.slug}/hints/rag_intro/dismiss/"
        resp = self.client.post(dismiss_url)
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["hints"]
        dismissed = next(h for h in data if h["id"] == "rag_intro")
        self.assertTrue(dismissed["dismissed"])
        state = AssistantHintState.objects.get(user=self.user, assistant=self.assistant, hint_id="rag_intro")
        assert state.completed_at is not None

    def test_tour_progress(self):
        progress_url = f"/api/assistants/{self.assistant.slug}/tour_progress/"
        resp = self.client.get(progress_url)
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body["total"], len(HINTS))
        self.assertEqual(body["completed"], 0)
        self.assertEqual(body["percent_complete"], 0)
        self.assertEqual(body["next_hint"], "rag_intro")

        self.client.post(
            f"/api/assistants/{self.assistant.slug}/hints/rag_intro/dismiss/"
        )

        resp = self.client.get(progress_url)
        body = resp.json()
        self.assertEqual(body["completed"], 1)
        self.assertEqual(body["next_hint"], "glossary_tour")
