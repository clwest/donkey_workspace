import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from assistants.models import Assistant
from agents.models import SignalEncodingArtifact


class Phase820APITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="u", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="A")

    def test_create_signal_artifact(self):
        resp = self.client.post(
            "/api/signal-artifacts/",
            {
                "source": self.assistant.id,
                "encoding_payload": "abc",
                "symbolic_origin": "myth",
                "modulation_tags": {},
                "receiver_scope": "all",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/signal-artifacts/")
        self.assertEqual(len(list_resp.json()), 1)

    def test_create_navigation_vector(self):
        resp = self.client.post(
            "/api/navigation-vectors/",
            {
                "assistant": self.assistant.id,
                "vector_path": ["a", "b"],
                "alignment_score": 0.7,
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/navigation-vectors/")
        self.assertEqual(len(list_resp.json()), 1)

    def test_create_flux_index(self):
        resp = self.client.post(
            "/api/flux-index/",
            {
                "swarm_scope": "global",
                "flux_measurements": {"entropy": 0.1},
                "insight_summary": "ok",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/flux-index/")
        self.assertEqual(len(list_resp.json()), 1)
