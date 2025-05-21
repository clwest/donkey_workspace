import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from unittest.mock import patch

from assistants.models import Assistant
from agents.models import SwarmMemoryEntry, LoreToken, Agent, LoreTokenCraftingRitual
from agents.utils.lore_token import (
    compress_memories_to_token,
    apply_lore_token_to_agent,
    perform_token_ritual,
)
from embeddings.models import EMBEDDING_LENGTH


class LoreTokenTest(TestCase):
    @patch("agents.utils.lore_token.get_embedding_for_text")
    @patch("agents.utils.lore_token.call_llm")
    def test_compress_memories_to_token(self, mock_call, mock_embed):
        mock_call.return_value = "summary"
        mock_embed.return_value = [0.1] * EMBEDDING_LENGTH
        assistant = Assistant.objects.create(name="A", specialty="x")
        m1 = SwarmMemoryEntry.objects.create(title="m1", content="c1")
        m2 = SwarmMemoryEntry.objects.create(title="m2", content="c2")
        token = compress_memories_to_token([m1, m2], assistant)
        self.assertEqual(token.summary, "summary")
        self.assertEqual(token.created_by, assistant)
        self.assertEqual(list(token.source_memories.all()), [m1, m2])
        self.assertEqual(len(token.embedding), EMBEDDING_LENGTH)

    @patch("agents.utils.lore_token.get_embedding_for_text")
    @patch("agents.utils.lore_token.call_llm")
    def test_compress_memories_with_type(self, mock_call, mock_embed):
        mock_call.return_value = "sum"
        mock_embed.return_value = [0.1] * EMBEDDING_LENGTH
        assistant = Assistant.objects.create(name="T", specialty="z")
        m = SwarmMemoryEntry.objects.create(title="m", content="c")
        token = compress_memories_to_token([m], assistant, token_type="prophecy")
        self.assertEqual(token.token_type, "prophecy")

    def test_apply_lore_token_to_agent(self):
        assistant = Assistant.objects.create(name="B", specialty="y")
        agent = Agent.objects.create(name="Agent", slug="ag", description="d")
        token = LoreToken.objects.create(
            name="t",
            summary="s",
            symbolic_tags={"skills": ["alpha"]},
            embedding=[0.0] * EMBEDDING_LENGTH,
            created_by=assistant,
        )
        apply_lore_token_to_agent(agent, token)
        self.assertIn("alpha", agent.skills)

    @patch("agents.utils.lore_token.get_embedding_for_text")
    @patch("agents.utils.lore_token.call_llm")
    def test_token_crafting_ritual(self, mock_call, mock_embed):
        mock_call.return_value = "ritual summary"
        mock_embed.return_value = [0.0] * EMBEDDING_LENGTH
        assistant = Assistant.objects.create(name="R", specialty="q")
        mem = SwarmMemoryEntry.objects.create(title="m", content="c")
        ritual = LoreTokenCraftingRitual.objects.create(
            initiating_assistant=assistant,
            symbolic_intent="test",
            token_type="echo",
        )
        ritual.base_memories.add(mem)
        token = perform_token_ritual(ritual)
        ritual.refresh_from_db()
        self.assertTrue(ritual.completed)
        self.assertEqual(ritual.resulting_token, token)
