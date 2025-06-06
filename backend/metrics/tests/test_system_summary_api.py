import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from rest_framework.test import APITestCase
from assistants.models import Assistant
from django.contrib.auth import get_user_model

class SystemSummaryAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="user", password="pw")
        self.client.force_authenticate(user=self.user)
        Assistant.objects.create(name="A", specialty="s", created_by=self.user)
        Assistant.objects.create(name="B", specialty="s", created_by=self.user, primary_badge="glossary_apprentice")

    def test_summary_endpoint(self):
        resp = self.client.get("/api/metrics/system/summary/")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["assistant_count"], 2)
