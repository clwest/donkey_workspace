import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from unittest.mock import patch, MagicMock

from agents.models import Agent, AgentSkill
from memory.models import MemoryEntry
from agents.utils.agent_collab_trainer import simulate_agent_skill_conversation


class SimulatedConversationTest(TestCase):
    def test_memory_logged(self):
        teacher = Agent.objects.create(name="Teacher", slug="t")
        learner = Agent.objects.create(name="Learner", slug="l")
        skill = AgentSkill.objects.create(name="X")

        mock_resp = MagicMock()
        mock_choice = MagicMock()
        mock_choice.message.content = "Hello"
        mock_resp.choices = [mock_choice]

        with patch("openai.OpenAI") as mock_client:
            instance = mock_client.return_value
            instance.chat.completions.create.return_value = mock_resp
            simulate_agent_skill_conversation(teacher, learner, skill)

        self.assertEqual(MemoryEntry.objects.count(), 1)
        mem = MemoryEntry.objects.first()
        self.assertIn("Teacher taught Learner", mem.event)
        self.assertTrue(mem.linked_agents.filter(id=learner.id).exists())
