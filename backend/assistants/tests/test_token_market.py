import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from django.test import TestCase
from unittest.mock import patch

from assistants.models import Assistant, AssistantReputation
from agents.models import SwarmMemoryEntry, LoreToken, LoreTokenExchange, TokenMarket
from agents.utils.lore_token import compress_memories_to_token
from embeddings.models import EMBEDDING_LENGTH


class TokenMarketReputationTest(TestCase):
    @patch("agents.utils.lore_token.get_embedding_for_text")
    @patch("agents.utils.lore_token.call_llm")
    def test_exchange_and_reputation(self, mock_call, mock_embed):
        mock_call.return_value = "sum"
        mock_embed.return_value = [0.1] * EMBEDDING_LENGTH
        a1 = Assistant.objects.create(name="A", specialty="x")
        a2 = Assistant.objects.create(name="B", specialty="y")
        m = SwarmMemoryEntry.objects.create(title="m", content="c")
        token = compress_memories_to_token([m], a1)
        rep1 = AssistantReputation.objects.get(assistant=a1)
        self.assertEqual(rep1.tokens_created, 1)
        self.assertEqual(rep1.reputation_score, 1)
        listing = TokenMarket.objects.create(token=token, listed_by=a1, visibility="public")
        self.assertIn(listing, TokenMarket.objects.filter(visibility="public"))
        LoreTokenExchange.objects.create(token=token, sender=a1, receiver=a2, intent="gift", context="here")
        rep1.refresh_from_db()
        rep2 = AssistantReputation.objects.get(assistant=a2)
        self.assertEqual(rep1.tokens_endorsed, 1)
        self.assertEqual(rep1.reputation_score, 2)
        self.assertEqual(rep2.tokens_received, 1)
        self.assertEqual(rep2.reputation_score, 1)
