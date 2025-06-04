from assistants.tests import BaseAPITestCase
from assistants.models import Assistant, AssistantBootLog
from intel_core.models import Document
from prompts.models import Prompt
from mcp_core.models import Tag, PromptUsageLog


class AvailablePromptsAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        self.assistant = Assistant.objects.create(name="Switch", specialty="s")
        self.tag = Tag.objects.create(
            name=self.assistant.name, slug=self.assistant.slug
        )
        self.doc = Document.objects.create(title="Doc", content="x", source_type="text")
        self.assistant.documents.add(self.doc)
        self.prompt1 = Prompt.objects.create(title="Tagged", content="a", source="t")
        self.prompt1.tags.add(self.tag)
        self.prompt2 = Prompt.objects.create(
            title="Linked", content="b", source="t", assistant=self.assistant
        )
        self.prompt3 = Prompt.objects.create(
            title="DocLinked", content="c", source="t", source_document=self.doc
        )
        PromptUsageLog.objects.create(
            prompt=self.prompt1,
            prompt_slug=self.prompt1.slug,
            prompt_title=self.prompt1.title,
            used_by="test",
        )
        self.url = f"/api/v1/assistants/{self.assistant.slug}/available_prompts/"

    def test_available_prompts(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 3)
        for item in data:
            self.assertIn("token_count", item)
            self.assertIn("usage_logs", item)


class UpdatePromptAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        self.prompt1 = Prompt.objects.create(title="Old", content="o", source="t")
        self.prompt2 = Prompt.objects.create(title="New", content="n", source="t")
        self.assistant = Assistant.objects.create(
            name="UP",
            specialty="x",
            system_prompt=self.prompt1,
            prompt_title=self.prompt1.title,
        )
        AssistantBootLog.objects.create(
            assistant=self.assistant, passed=False, report="r"
        )
        self.url = f"/api/v1/assistants/{self.assistant.slug}/update_prompt/"

    def test_update_prompt(self):
        resp = self.client.patch(
            self.url, {"prompt_id": str(self.prompt2.id)}, format="json"
        )
        self.assertEqual(resp.status_code, 200)
        self.assistant.refresh_from_db()
        self.assertEqual(self.assistant.system_prompt, self.prompt2)
        self.assertEqual(self.assistant.prompt_title, self.prompt2.title)
        self.assertEqual(self.assistant.boot_logs.count(), 0)
