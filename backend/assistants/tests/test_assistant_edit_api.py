from assistants.tests import BaseAPITestCase
from assistants.models import Assistant
from prompts.models import Prompt

class AssistantEditAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        self.assistant = Assistant.objects.create(name="EditA", specialty="x")
        self.prompt = Prompt.objects.create(title="p", content="c", source="t")
        self.url = f"/api/v1/assistants/{self.assistant.slug}/"

    def test_edit_fields(self):
        payload = {"tone": "friendly", "preferred_model": "gpt-4", "system_prompt": str(self.prompt.id)}
        resp = self.client.patch(self.url, payload, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assistant.refresh_from_db()
        self.assertEqual(self.assistant.tone, "friendly")
        self.assertEqual(self.assistant.preferred_model, "gpt-4")
        self.assertEqual(self.assistant.system_prompt, self.prompt)

