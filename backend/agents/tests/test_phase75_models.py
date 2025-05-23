import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant, AssistantGuild
from agents.models import SwarmCodex, AgentAwareCodex, SymbolicCoordinationEngine
from agents.utils.ritual_network import generate_ritual_from_ecosystem_state


class Phase75ModelTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="A")
        self.guild = AssistantGuild.objects.create(name="G")
        self.codex = SwarmCodex.objects.create(
            title="C", created_by=self.assistant, symbolic_domain="order"
        )

    def test_agent_aware_codex(self):
        aware = AgentAwareCodex.objects.create(
            base_codex=self.codex,
            codex_awareness_map={"a": {"compliance": 1}},
            sentiment_trend="steady",
            evolving_clauses={"c1": "rule"},
        )
        self.assertEqual(aware.base_codex, self.codex)
        self.assertIn("a", aware.codex_awareness_map)

    def test_symbolic_coordination_engine(self):
        engine = SymbolicCoordinationEngine.objects.create(
            guild=self.guild,
            active_signals={"entropy": 0.1},
            coordination_strategy="sync",
            tasks_assigned={},
        )
        self.assertEqual(engine.guild, self.guild)

    def test_generate_ritual(self):
        ritual = generate_ritual_from_ecosystem_state()
        self.assertIn("name", ritual)
        self.assertIn("steps", ritual)
