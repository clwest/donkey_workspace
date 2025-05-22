
from assistants.tests import BaseAPITestCase
from unittest.mock import patch
import uuid
from assistants.models import Assistant


class PersonaTraitsPromptTest(BaseAPITestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(
            name="TraitBot",
            specialty="testing",
            traits=["cautious", "curious"],
            tone="sassy",
            persona_mode="improviser",
        )
        self.url = f"/api/v1/assistants/{self.assistant.slug}/chat/"

    def _make_completion(self):
        class Msg:
            content = "ok"

        class Choice:
            message = Msg()

        class Usage:
            prompt_tokens = 1
            completion_tokens = 1
            total_tokens = 2

        class Completion:
            def __init__(self):
                self.choices = [Choice()]
                self.usage = Usage()

        return Completion()

    @patch("assistants.views.assistants.client.chat.completions.create")
    def test_traits_and_tone_in_prompt(self, mock_create):
        captured = {}

        def side_effect(**kwargs):
            captured["messages"] = kwargs.get("messages")
            return self._make_completion()

        mock_create.side_effect = side_effect
        self.client.post(
            self.url,
            {"message": "hi", "session_id": str(uuid.uuid4())},
            format="json",
        )
        system_prompt = captured["messages"][0]["content"]
        self.assertIn("Traits: cautious, curious", system_prompt)
        self.assertIn("Tone: sassy", system_prompt)
        self.assertIn("Mode: improviser", system_prompt)
