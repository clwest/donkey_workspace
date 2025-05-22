
from django.contrib.auth import get_user_model
from assistants.tests import BaseAPITestCase
from unittest.mock import patch
from assistants.models import (
    Assistant,
    AssistantProject,
    AssistantMemoryChain,
    AssistantReflectionLog,
)
from memory.models import MemoryEntry
from mcp_core.models import Tag


class ReflectOnMemoryChainAPITest(BaseAPITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="t", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="A", specialty="t")
        self.project = AssistantProject.objects.create(
            assistant=self.assistant, title="P"
        )
        self.tag = Tag.objects.create(name="One", slug="one")
        mem = MemoryEntry.objects.create(
            event="m1", assistant=self.assistant, related_project=self.project
        )
        mem.tags.add(self.tag)
        self.chain = AssistantMemoryChain.objects.create(
            project=self.project, title="C"
        )
        self.chain.memories.add(mem)
        self.chain.filter_tags.add(self.tag)

    @patch(
        "assistants.utils.assistant_reflection_engine.AssistantReflectionEngine.generate_reflection"
    )
    def test_reflection_endpoint(self, mock_gen):
        mock_gen.return_value = "sum"
        url = f"/api/assistants/{self.assistant.slug}/reflect/chain/"
        resp = self.client.post(url, {"chain_id": str(self.chain.id)}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["summary"], "sum")
        self.assertEqual(
            AssistantReflectionLog.objects.filter(assistant=self.assistant).count(), 1
        )
