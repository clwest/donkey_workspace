import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from assistants.models import Assistant
from agents.models import RitualArchiveEntry
from agents.models.lore import SwarmCodex, DialogueCodexMutationLog
from agents.models.federation import SwarmFederationEngine
from agents.models.identity import SymbolicIdentityCard
from metrics.models import RitualPerformanceMetric
from simulation.models import MythScenarioSimulator, MythflowSession


class WorldDashboardAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="user", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="A", specialty="s")
        self.codex = SwarmCodex.objects.create(
            title="C", created_by=self.assistant, symbolic_domain="myth"
        )
        SymbolicIdentityCard.objects.create(
            assistant=self.assistant,
            archetype="Hero",
            symbolic_tags={},
            myth_path="",
            purpose_signature="",
        )
        self.ritual = RitualArchiveEntry.objects.create(name="R", ceremony_type="t")
        RitualPerformanceMetric.objects.create(
            ritual=self.ritual,
            assistant=self.assistant,
            symbolic_score=1.0,
            transformation_alignment=1.0,
            mythic_tags={},
            reflection_notes="ok",
        )
        engine = SwarmFederationEngine.objects.create(
            symbolic_state_map={"entropy": 0.2},
            federation_log="log",
            ritual_convergence_score=0.8,
        )
        engine.active_guilds.set([])
        DialogueCodexMutationLog.objects.create(
            codex=self.codex,
            triggering_dialogue="hi",
            mutation_reason="test",
            symbolic_impact={},
        )
        sim = MythScenarioSimulator.objects.create(
            simulation_title="sim",
            initiating_entity=self.assistant,
            selected_archetypes={},
            narrative_goals="",
        )
        session = MythflowSession.objects.create(
            session_name="s", active_scenario=sim
        )
        session.participants.add(self.assistant)
        session.live_codex_context.add(self.codex)

    def test_world_metrics(self):
        resp = self.client.get("/api/metrics/world-metrics/")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("active_assistants", resp.json())

    def test_assistant_presence(self):
        resp = self.client.get("/api/metrics/assistant-presence/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()[0]["archetype"], "Hero")

    def test_heatmap(self):
        resp = self.client.get("/api/metrics/mythflow-heatmap/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()[0]["title"], "C")
