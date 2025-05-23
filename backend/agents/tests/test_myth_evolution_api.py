import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase


class MythEvolutionAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="user", password="pw")
        self.client.force_authenticate(user=self.user)

    def test_evolution_endpoint(self):
        resp = self.client.post("/api/myth-evolution/", {})
        self.assertEqual(resp.status_code, 201)
        self.assertIn("entropy", resp.json())
