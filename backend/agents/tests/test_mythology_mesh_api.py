import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from assistants.models import Assistant
from agents.models import MythologyMeshNode, ArchetypalDriftForecast


class MythologyMeshAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="mesh", password="pw")
        self.client.force_authenticate(user=self.user)
        self.a1 = Assistant.objects.create(name="A1", specialty="logic")
        self.a2 = Assistant.objects.create(name="A2", specialty="art")

    def test_create_and_list_mesh_nodes(self):
        resp = self.client.post(
            "/api/mythology-mesh/",
            {
                "assistant": self.a1.id,
                "connected_to": [self.a2.id],
                "link_reason": {"shared_myth": True},
                "mythic_distance_score": 0.5,
            },
        )
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(MythologyMeshNode.objects.count(), 1)

        resp = self.client.get("/api/mythology-mesh/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 1)

    def test_constellation_map(self):
        resp = self.client.get("/api/constellation-map/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("clusters", resp.json())


class ArchetypalDriftAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="drift", password="pw")
        self.client.force_authenticate(user=self.user)
        self.a1 = Assistant.objects.create(name="A3", specialty="dream")

    def test_create_and_list_forecasts(self):
        resp = self.client.post(
            "/api/archetype-drift/",
            {
                "assistant": self.a1.id,
                "observed_archetype": "guide",
                "predicted_archetype": "sage",
                "drift_score": 0.7,
                "prediction_basis": "test",
            },
        )
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(ArchetypalDriftForecast.objects.count(), 1)

        resp = self.client.get("/api/archetype-drift/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 1)
