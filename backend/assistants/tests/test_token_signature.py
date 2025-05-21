import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from hashlib import sha256
from assistants.models import Assistant, AssistantGuild, AssistantCivilization
from story.models import LoreEntry
from agents.models import (
    SwarmMemoryEntry,
    LoreToken,
    LoreTokenSignature,
    TemporalLoreAnchor,
    RitualComplianceRecord,
)
from agents.utils.lore_token import compress_memories_to_token
from agents.utils.myth_verification import verify_lore_token_signature, sync_chronomyth_state
from embeddings.models import EMBEDDING_LENGTH


class TokenSignatureTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="Signer", specialty="x")
        self.memory = SwarmMemoryEntry.objects.create(title="m", content="c")
        self.token = compress_memories_to_token([self.memory], self.assistant)

    def test_verify_signature(self):
        sig_value = sha256("c".encode()).hexdigest()
        sig = LoreTokenSignature.objects.create(
            token=self.token, signed_by=self.assistant, signature=sig_value
        )
        result = verify_lore_token_signature(self.token)
        sig.refresh_from_db()
        self.assertTrue(result)
        self.assertTrue(sig.verified)


class ChronomythSyncTest(TestCase):
    def setUp(self):
        lore = LoreEntry.objects.create(title="root", content="x")
        self.assistant = Assistant.objects.create(name="Syncer", specialty="y")
        guild = AssistantGuild.objects.create(name="G", founding_myth=lore)
        self.civ = AssistantCivilization.objects.create(
            name="C", myth_root=lore, symbolic_domain="d"
        )
        self.civ.founding_guilds.add(guild)
        self.token = LoreToken.objects.create(
            name="t",
            summary="s",
            symbolic_tags={},
            embedding=[0.0] * EMBEDDING_LENGTH,
            created_by=self.assistant,
        )
        self.anchor = TemporalLoreAnchor.objects.create(
            anchor_type="equinox",
            timestamp=django.utils.timezone.now(),
            narrative_impact_summary="i",
        )
        self.anchor.attached_tokens.add(self.token)

    def test_sync_creates_records(self):
        sync_chronomyth_state()
        self.assertTrue(
            RitualComplianceRecord.objects.filter(
                civilization=self.civ, anchor=self.anchor
            ).exists()
        )
