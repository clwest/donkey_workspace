import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant, AssistantGuild
from agents.models import (
    SwarmMemoryEntry,
    LoreToken,
    TokenArbitrationSession,
    SymbolicConflict,
    LorechainLink,
)
from embeddings.models import EMBEDDING_LENGTH


class SymbolicModelsTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="A", specialty="x")
        self.guild1 = AssistantGuild.objects.create(name="G1")
        self.guild2 = AssistantGuild.objects.create(name="G2")
        self.token = LoreToken.objects.create(
            name="t",
            summary="s",
            symbolic_tags={},
            embedding=[0.0] * EMBEDDING_LENGTH,
            created_by=self.assistant,
        )
        self.memory = SwarmMemoryEntry.objects.create(title="m", content="c")

    def test_token_arbitration_session(self):
        sess = TokenArbitrationSession.objects.create(
            token=self.token,
            conflict_type="ownership",
            initiating_guild=self.guild1,
        )
        sess.guilds.add(self.guild1, self.guild2)
        self.assertEqual(sess.guilds.count(), 2)
        self.assertEqual(sess.initiating_guild, self.guild1)
        self.assertEqual(sess.outcome, "pending")

    def test_symbolic_conflict_creation(self):
        conflict = SymbolicConflict.objects.create(
            topic="test", symbolic_position_map={"a": "b"}
        )
        conflict.participating_assistants.add(self.assistant)
        conflict.memory_context.add(self.memory)
        conflict.token_context.add(self.token)
        self.assertEqual(conflict.participating_assistants.count(), 1)
        self.assertEqual(conflict.memory_context.count(), 1)
        self.assertEqual(conflict.token_context.count(), 1)

    def test_lorechain_link(self):
        descendant = LoreToken.objects.create(
            name="child",
            summary="d",
            symbolic_tags={},
            embedding=[0.0] * EMBEDDING_LENGTH,
            created_by=self.assistant,
        )
        link = LorechainLink.objects.create(
            source_token=self.token,
            descendant_token=descendant,
            mutation_type="refinement",
            symbolic_inheritance_notes="notes",
        )
        self.assertEqual(link.source_token, self.token)
        self.assertEqual(link.descendant_token, descendant)
