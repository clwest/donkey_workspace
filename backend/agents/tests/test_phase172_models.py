import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from agents.models import (
    SwarmCodex,
    CodexLinkedGuild,
    CodexFederationArchitecture,
    NarrativeLawSystem,
    SymbolicTreatyProtocol,
)


class Phase172ModelsTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="A")
        self.codex = SwarmCodex.objects.create(
            title="C", created_by=self.assistant, symbolic_domain="myth"
        )
        self.guild = CodexLinkedGuild.objects.create(
            guild_name="G",
            anchor_codex=self.codex,
            member_users={},
            ritual_focus={},
            codex_compliance_score=0.9,
        )
        self.guild.member_assistants.add(self.assistant)

    def test_federation_architecture(self):
        federation = CodexFederationArchitecture.objects.create(
            federation_name="F",
            governance_rules={},
            federation_mandates="m",
        )
        federation.founding_codices.add(self.codex)
        federation.assistant_moderators.add(self.assistant)
        self.assertEqual(federation.founding_codices.count(), 1)
        self.assertEqual(federation.assistant_moderators.count(), 1)

    def test_narrative_law_system(self):
        federation = CodexFederationArchitecture.objects.create(
            federation_name="F2",
            governance_rules={},
            federation_mandates="m",
        )
        law = NarrativeLawSystem.objects.create(
            federation=federation,
            ritual_law_map={},
            symbolic_penalties={},
            codex_enforcement_routes="r",
        )
        law.assistant_role_enactors.add(self.assistant)
        self.assertEqual(law.federation, federation)
        self.assertEqual(law.assistant_role_enactors.count(), 1)

    def test_symbolic_treaty_protocol(self):
        treaty = SymbolicTreatyProtocol.objects.create(
            treaty_title="T",
            codex_shared_clauses={},
            ritual_bond_requirements={},
            symbolic_enforcement_terms="e",
            treaty_status="draft",
        )
        treaty.participating_guilds.add(self.guild)
        self.assertEqual(treaty.participating_guilds.count(), 1)

