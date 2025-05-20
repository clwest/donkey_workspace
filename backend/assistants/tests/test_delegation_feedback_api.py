import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from assistants.models import Assistant, DelegationEvent


class DelegationFeedbackAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="rater", password="pw")
        self.client.force_authenticate(user=self.user)
        self.parent = Assistant.objects.create(name="Parent", specialty="root")
        self.child = Assistant.objects.create(name="Child", specialty="worker")
        self.event = DelegationEvent.objects.create(
            parent_assistant=self.parent,
            child_assistant=self.child,
            reason="testing",
        )

    def test_submit_feedback(self):
        url = f"/api/assistants/delegation/{self.event.id}/feedback/"
        payload = {"score": 4, "trust_label": "trusted", "notes": "good"}
        resp = self.client.post(url, payload, format="json")
        self.assertEqual(resp.status_code, 200)
        self.event.refresh_from_db()
        self.assertEqual(self.event.score, 4)
        self.assertEqual(self.event.trust_label, "trusted")
        self.assertEqual(self.event.notes, "good")
