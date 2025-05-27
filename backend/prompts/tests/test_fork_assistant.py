import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from prompts.models import Prompt, PromptMutationLog
from prompts.utils.mutation import fork_assistant_from_prompt


class ForkAssistantFromPromptTest(TestCase):
    def setUp(self):
        self.prompt = Prompt.objects.create(title="Base", content="Hi", source="unit")
        self.assistant = Assistant.objects.create(name="Base", system_prompt=self.prompt)

    def test_fork_creates_mutation_log(self):
        fork_assistant_from_prompt(self.assistant, "New system prompt")
        log = PromptMutationLog.objects.get(original_prompt=self.prompt)
        self.assertEqual(log.mutated_text, "New system prompt")
        self.assertEqual(log.mode, "fork")
