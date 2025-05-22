
from django.contrib.auth import get_user_model
from assistants.tests import BaseAPITestCase
from assistants.models import Assistant, DelegationEvent
from memory.models import MemoryEntry
from mcp_core.models import Tag


class SuggestDelegationAPITest(BaseAPITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="rec", password="pw")
        self.client.force_authenticate(self.user)
        self.parent = Assistant.objects.create(name="Parent", specialty="general")
        self.candidate = Assistant.objects.create(name="TTS", specialty="tts")
        self.memory = MemoryEntry.objects.create(event="m", assistant=self.parent)
        tag = Tag.objects.create(name="tts", slug="tts")
        self.memory.tags.add(tag)
        DelegationEvent.objects.create(
            parent_assistant=self.parent,
            child_assistant=self.candidate,
            score=5,
            trust_label="trusted",
        )
        self.url = f"/api/assistants/{self.parent.slug}/suggest-delegation/"

    def test_tag_match(self):
        resp = self.client.post(
            self.url, {"context_type": "memory", "context_id": str(self.memory.id)}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["recommended_assistant"]["slug"], self.candidate.slug)

    def test_includes_trust_label(self):
        resp = self.client.post(
            self.url, {"context_type": "memory", "context_id": str(self.memory.id)}
        )
        self.assertIn("trust_label", resp.json()["recommended_assistant"])

    def test_no_match_fallback(self):
        Assistant.objects.filter(id=self.candidate.id).delete()
        resp = self.client.post(
            self.url, {"context_type": "memory", "context_id": str(self.memory.id)}
        )
        data = resp.json()
        self.assertIsNone(data["recommended_assistant"])
        self.assertIn("message", data)

