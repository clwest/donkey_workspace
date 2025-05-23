import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from agents.models import (
    CodexLinkedGuild,
    SwarmCodex,
    SymbolicConsensusChamber,
    RitualNegotiationEngine,
    NarrativeGovernanceModel,
)


class Phase151ModelTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="A")
        self.codex = SwarmCodex.objects.create(
            title="C", created_by=self.assistant, symbolic_domain="myth"
        )
        self.guild = CodexLinkedGuild.objects.create(
            guild_name="G", anchor_codex=self.codex, codex_compliance_score=1.0
        )

    def test_symbolic_consensus_chamber(self):
        chamber = SymbolicConsensusChamber.objects.create(
            chamber_title="T",
            active_codex=self.codex,
            ritual_petitions={},
            belief_vote_matrix={},
            consensus_summary="S",
        )
        chamber.guilds_involved.add(self.guild)
        self.assertEqual(chamber.chamber_title, "T")
        self.assertIn(self.guild, chamber.guilds_involved.all())

    def test_ritual_negotiation_engine(self):
        engine = RitualNegotiationEngine.objects.create(
            assistant_role_signatures={},
            codex_conflict_index={},
            ritual_interaction_logs={},
        )
        self.assertIsNone(engine.codex_drift_score)

    def test_narrative_governance_model(self):
        model = NarrativeGovernanceModel.objects.create(
            governance_title="N",
            ruling_guild=self.guild,
            symbolic_policy="P",
            codex_weight_map={},
            ritual_rotation_sequence=[],
            memory_impact_log="log",
        )
        self.assertEqual(model.ruling_guild, self.guild)
