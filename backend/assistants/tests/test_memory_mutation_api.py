
from django.contrib.auth import get_user_model
from assistants.tests import BaseAPITestCase
from assistants.models import Assistant
from memory.models import MemoryEntry


class MemoryMutationAPITest(BaseAPITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="tester", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="A", specialty="s")
        self.memory = MemoryEntry.objects.create(
            event="Original event",
            summary="Original summary",
            assistant=self.assistant,
        )

    def test_mutate_memory_endpoint(self):
        url = f"/api/v1/memory/{self.memory.id}/mutate/"
        resp = self.client.post(url, {"style": "clarify"}, format="json")
        self.assertEqual(resp.status_code, 201)
        data = resp.json()
        self.assertEqual(data["parent_memory"], str(self.memory.id))
        self.assertEqual(data["type"], "mutation")
        self.assertTrue(MemoryEntry.objects.filter(parent_memory=self.memory).exists())
