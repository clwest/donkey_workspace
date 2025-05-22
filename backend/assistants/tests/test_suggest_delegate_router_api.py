
from django.contrib.auth import get_user_model
from assistants.tests import BaseAPITestCase
from unittest.mock import patch

from assistants.models import Assistant, AssistantThoughtLog
from memory.models import MemoryEntry
from embeddings.models import EMBEDDING_LENGTH


class SuggestDelegateRouterAPITest(BaseAPITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="router", password="pw")
        self.client.force_authenticate(self.user)
        self.parent = Assistant.objects.create(name="Parent", specialty="general")
        self.c1 = Assistant.objects.create(name="Tech", specialty="code")
        self.c2 = Assistant.objects.create(name="Docs", specialty="docs")
        self.c1.capability_embedding = [1.0] * EMBEDDING_LENGTH
        self.c1.save()
        self.c2.capability_embedding = [0.5] * EMBEDDING_LENGTH
        self.c2.save()
        self.mem = MemoryEntry.objects.create(event="github issue triage", assistant=self.parent)
        self.url = "/api/assistants/suggest_delegate/"

    @patch("assistants.utils.delegation_router.get_embedding_for_text")
    def test_returns_ranked(self, mock_emb):
        mock_emb.return_value = [1.0] * EMBEDDING_LENGTH
        resp = self.client.post(self.url, {"memory_id": str(self.mem.id)}, format="json")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["suggestions"]
        self.assertEqual(data[0]["slug"], self.c1.slug)

    @patch("assistants.utils.delegation_router.get_embedding_for_text")
    def test_logs_suggestion(self, mock_emb):
        mock_emb.return_value = [1.0] * EMBEDDING_LENGTH
        resp = self.client.post(
            self.url,
            {"memory_id": str(self.mem.id), "assistant_slug": self.parent.slug},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        log = AssistantThoughtLog.objects.filter(
            assistant=self.parent, thought_type="delegation_suggestion"
        ).first()
        self.assertIsNotNone(log)
