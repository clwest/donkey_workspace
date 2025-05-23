import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from agents.models import (
    MythWeavingProtocol,
    SymbolicResourceRegistry,
    DreamEconomyFoundation,
    AssistantPolity,
    SwarmCodex,
)


class Phase86ModelTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="Alpha")
        self.codex = SwarmCodex.objects.create(
            title="C", created_by=self.assistant, symbolic_domain="core"
        )
        self.polity = AssistantPolity.objects.create(
            name="P", founding_codex=self.codex, core_purpose_statement="p"
        )

    def test_myth_weaving_protocol(self):
        proto = MythWeavingProtocol.objects.create(
            initiator=self.assistant,
            narrative_theme="Hero",
            symbolic_artifacts_used={"a": 1},
            final_myth_product="story",
        )
        proto.involved_assistants.add(self.assistant)
        self.assertEqual(proto.narrative_theme, "Hero")
        self.assertIn(self.assistant, proto.involved_assistants.all())

    def test_symbolic_resource_registry(self):
        res = SymbolicResourceRegistry.objects.create(
            resource_type="token",
            unique_id="u1",
            ownership=self.polity,
            access_policy="open",
            symbolic_lineage={},
        )
        self.assertEqual(res.resource_type, "token")
        self.assertEqual(res.ownership, self.polity)

    def test_dream_economy_foundation(self):
        econ = DreamEconomyFoundation.objects.create(
            economy_scope="guild",
            symbolic_valuation_model={},
            reputation_inputs={},
            legacy_conversion_rate=1.0,
            governance_policies="none",
        )
        self.assertEqual(econ.economy_scope, "guild")
