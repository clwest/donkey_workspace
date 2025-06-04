from unittest.mock import patch
from assistants.tests import BaseAPITestCase
from assistants.models import Assistant
from prompts.models import Prompt
from utils import llm_router
from assistants.utils.core_assistant import CoreAssistant


class PromptReflectionTest(BaseAPITestCase):
    def setUp(self):
        self.prompt1 = Prompt.objects.create(title="P1", content="First", token_count=1)
        self.prompt2 = Prompt.objects.create(title="P2", content="Second", token_count=1)
        self.assistant = Assistant.objects.create(name="A", system_prompt=self.prompt1)

    @patch("utils.llm_router.call_llm", return_value="ok")
    @patch("utils.llm_router.get_relevant_chunks", return_value=([], None, False, False, 0.0, None, False, False, [], {}))
    def test_chat_uses_latest_prompt(self, mock_get, mock_call):
        llm_router.chat([{"role": "user", "content": "hi"}], self.assistant)
        Assistant.objects.filter(id=self.assistant.id).update(system_prompt=self.prompt2)
        llm_router.chat([{"role": "user", "content": "hi"}], self.assistant)
        first = mock_call.call_args_list[0][0][0][0]["content"]
        second = mock_call.call_args_list[1][0][0][0]["content"]
        assert "First" in first
        assert "Second" in second

    def test_coreassistant_refreshes_prompt(self):
        ca = CoreAssistant(self.assistant)
        self.assertEqual(ca.get_system_prompt(), "First")
        Assistant.objects.filter(id=self.assistant.id).update(system_prompt=self.prompt2)
        self.assertEqual(ca.get_system_prompt(), "Second")
