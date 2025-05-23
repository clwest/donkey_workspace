import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from agents.models import (
    SwarmCodex,
    SwarmMemoryEntry,
    SymbolicRoadmapPlan,
    CommunityMythPlanningArena,
    FederatedCodexForecastTool,
)


class Phase136ModelsTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="A")
        self.codex = SwarmCodex.objects.create(
            title="C", created_by=self.assistant, symbolic_domain="myth"
        )
        self.memory = SwarmMemoryEntry.objects.create(title="M", content="c")

    def test_symbolic_roadmap_plan(self):
        plan = SymbolicRoadmapPlan.objects.create(
            plan_title="Plan",
            contributors=["u1"],
            archetype_path=["hero"],
            ritual_checkpoints=[1],
        )
        plan.codex_constraints.add(self.codex)
        plan.memory_segments.add(self.memory)
        self.assertEqual(plan.codex_constraints.count(), 1)
        self.assertEqual(plan.memory_segments.count(), 1)

    def test_community_myth_planning_arena(self):
        arena = CommunityMythPlanningArena.objects.create(
            arena_title="Arena",
            participant_ids=["u1"],
            myth_proposals={},
            symbolic_tension_points={},
        )
        arena.codex_focus.add(self.codex)
        self.assertEqual(arena.codex_focus.count(), 1)

    def test_federated_codex_forecast_tool(self):
        tool = FederatedCodexForecastTool.objects.create(
            forecast_title="F",
            narrative_pressure_map={},
            projected_mutation_events={},
            convergence_score=0.5,
        )
        tool.codex_inputs.add(self.codex)
        self.assertEqual(tool.codex_inputs.count(), 1)
