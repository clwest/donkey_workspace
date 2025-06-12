import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.test_settings")
import django

django.setup()

from django.test import TestCase
from rest_framework.test import APIClient
from memory.models import MemoryEntry, MemoryFeedback


class MemoryFeedbackStatusTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.memory = MemoryEntry.objects.create(event="test")

    def test_create_and_filter_feedback_by_status(self):
        url = "/api/v1/memory/memory/feedback/submit/"
        resp = self.client.post(
            url,
            {
                "memory": str(self.memory.id),
                "suggestion": "fix",
                "status": "pending",
                "rating": 5,
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)

        resp = self.client.post(
            url,
            {
                "memory": str(self.memory.id),
                "suggestion": "ok",
                "status": "accepted",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)

        list_url = f"/api/v1/memory/memory/{self.memory.id}/feedback/"
        resp = self.client.get(list_url)
        self.assertEqual(len(resp.data), 2)

        resp = self.client.get(list_url + "?status=pending")
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]["status"], "pending")

        resp = self.client.get(list_url + "?status=accepted")
        self.assertEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]["status"], "accepted")
