import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from agents.models import (
    CosmologicalRole,
    TranscendentMyth,
    LegacyTokenVault,
    LoreToken,
    AssistantPolity,
)
from embeddings.models import EMBEDDING_LENGTH


class Phase56ModelTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="A")
        self.myth = TranscendentMyth.objects.create(name="Myth")
        self.polity = AssistantPolity.objects.create(name="P")

    def test_cosmological_role(self):
        role = CosmologicalRole.objects.create(
            name="Hero",
            symbolic_traits={"brave": True},
            myth_origin=self.myth,
            phase_map={"creation": "rise"},
        )
        role.bound_assistants.add(self.assistant)
        self.assertEqual(role.bound_assistants.count(), 1)
        self.assertEqual(role.name, "Hero")

    def test_legacy_token_vault(self):
        token = LoreToken.objects.create(
            name="T",
            summary="s",
            symbolic_tags={},
            embedding=[0.0] * EMBEDDING_LENGTH,
            created_by=self.assistant,
        )
        vault = LegacyTokenVault.objects.create(
            name="Vault",
            stewarded_by=self.polity,
            vault_access_policy="public",
        )
        vault.preserved_tokens.add(token)
        self.assertEqual(vault.preserved_tokens.count(), 1)
