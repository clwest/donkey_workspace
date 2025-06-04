from django.contrib.auth import get_user_model
from assistants.tests import BaseAPITestCase
from assistants.models import Assistant, AssistantReflectionLog
from intel_core.models import Document
from memory.models import MemoryEntry
from prompts.models import Prompt


class AssistantBootProfileAPITest(BaseAPITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="boot", password="pw")
        self.client.force_authenticate(user=self.user)
        prompt = Prompt.objects.create(title="Sys", content="hi", token_count=5)
        self.assistant = Assistant.objects.create(name="Boot", specialty="b", system_prompt=prompt)
        doc = Document.objects.create(title="Doc", content="c", source_url="http://x.com")
        self.assistant.documents.add(doc)
        MemoryEntry.objects.create(event="m", assistant=self.assistant)
        AssistantReflectionLog.objects.create(assistant=self.assistant, summary="s")

    def test_boot_profile_endpoint(self):
        url = f"/api/v1/assistants/{self.assistant.slug}/boot_profile/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["assistant_id"], str(self.assistant.id))
        self.assertEqual(data["system_prompt"]["title"], "Sys")

    def test_self_test_endpoint(self):
        url = f"/api/v1/assistants/{self.assistant.slug}/selftest/"
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["passed"])
        self.assertEqual(data["issues"], [])
