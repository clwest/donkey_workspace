import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from assistants.models import Assistant, AssistantThoughtLog, DelegationEvent
from memory.models import MemoryEntry


class PrimaryAssistantActionsAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="viewer", password="pw")
        self.client.force_authenticate(user=self.user)
        self.primary = Assistant.objects.create(name="Boss", specialty="manage", is_primary=True)
        self.memory = MemoryEntry.objects.create(event="hello", assistant=self.primary)

    def test_primary_reflect_now(self):
        url = "/api/assistants/primary/reflect-now/"
        resp = self.client.post(url, {"memory_id": str(self.memory.id)}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(AssistantThoughtLog.objects.filter(assistant=self.primary).count(), 1)

    def test_primary_spawn_agent(self):
        url = "/api/assistants/primary/spawn-agent/"
        resp = self.client.post(url, {"memory_id": str(self.memory.id), "reason": "test"}, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(DelegationEvent.objects.count(), 1)
        self.assertEqual(Assistant.objects.filter(parent_assistant=self.primary).count(), 1)
