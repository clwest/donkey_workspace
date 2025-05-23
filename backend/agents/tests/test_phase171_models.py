import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from agents.models import (
    SwarmCodex,
    EncodedRitualBlueprint,
    CodexLinkedGuild,
    AssistantDiplomacyInterface,
    CodexConvergenceCeremony,
    MythicArbitrationCouncil,
)


class Phase171ModelTest(TestCase):
    def setUp(self):
        self.a1 = Assistant.objects.create(name="A1")
        self.a2 = Assistant.objects.create(name="A2")
        self.codex1 = SwarmCodex.objects.create(
            title="C1", created_by=self.a1, symbolic_domain="myth"
        )
        self.codex2 = SwarmCodex.objects.create(
            title="C2", created_by=self.a1, symbolic_domain="myth"
        )
        self.ritual = EncodedRitualBlueprint.objects.create(name="R", encoded_steps={})
        self.guild = CodexLinkedGuild.objects.create(
            guild_name="G", anchor_codex=self.codex1, codex_compliance_score=1.0
        )

    def test_assistant_diplomacy_interface(self):
        interf = AssistantDiplomacyInterface.objects.create(
            initiator=self.a1,
            target=self.a2,
            proposal_type="codex_merge",
            dialogue_log="log",
            diplomatic_outcome="pending",
            symbolic_agreement_score=0.5,
        )
        self.assertEqual(interf.initiator, self.a1)
        self.assertEqual(interf.target, self.a2)

    def test_codex_convergence_ceremony(self):
        ceremony = CodexConvergenceCeremony.objects.create(
            ceremony_title="Merge",
            symbolic_thresholds={},
        )
        ceremony.converging_codices.add(self.codex1, self.codex2)
        ceremony.ritual_chain.add(self.ritual)
        self.assertEqual(ceremony.converging_codices.count(), 2)
        self.assertEqual(ceremony.ritual_chain.count(), 1)

    def test_mythic_arbitration_council(self):
        council = MythicArbitrationCouncil.objects.create(
            council_title="Council",
            belief_dispute_summary="sum",
            council_votes={"G": 1},
            resolved_codex_adjustments={},
        )
        council.member_guilds.add(self.guild)
        self.assertEqual(council.member_guilds.count(), 1)
