from unittest.mock import patch
from assistants.tests import BaseAPITestCase
from assistants.models import Assistant
from memory.models import MemoryEntry
from insights.models import AssistantInsightLog


class ChatReflectionAPITest(BaseAPITestCase):
    @patch("assistants.utils.chat_reflection.complete_chat", return_value='{"summary":"sum","tags":["planning"],"proposed_prompt":"new"}')
    def test_chat_reflection_endpoint(self, mock_llm):
        self.authenticate()
        assistant = Assistant.objects.create(name="A", slug="a")
        MemoryEntry.objects.create(assistant=assistant, event="hi", summary="hi", is_conversation=True, source_role="user")
        url = f"/api/assistants/{assistant.slug}/reflect_on_chat/"
        resp = self.client.post(url)
        assert resp.status_code == 200
        assert AssistantInsightLog.objects.filter(assistant=assistant).count() == 1
        data = resp.json()
        assert data.get("summary") == "sum"
        assert data.get("tags") == ["planning"]
