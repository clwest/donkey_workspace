from django.contrib.auth import get_user_model
from assistants.tests import BaseAPITestCase
from assistants.models import Assistant
from memory.models import MemoryEntry


class AssistantUserReflectAPITest(BaseAPITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="test", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="Robo", specialty="test")

    def test_submit_feedback_creates_memory(self):
        url = f"/api/v1/assistants/{self.assistant.slug}/reflect/"
        resp = self.client.post(url, {"content": "Great job", "rating": 5}, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(MemoryEntry.objects.filter(assistant=self.assistant).count(), 1)

    def test_missing_content_returns_400(self):
        url = f"/api/v1/assistants/{self.assistant.slug}/reflect/"
        resp = self.client.post(url, {"rating": 3}, format="json")
        self.assertEqual(resp.status_code, 400)
