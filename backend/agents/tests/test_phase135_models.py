import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from agents.models import (
    SwarmCodex,
    SwarmMemoryEntry,
    RitualGoalPlanner,
    MythTimelineDirector,
    CodexDecisionFramework,
)


class Phase135ModelTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="Alpha", specialty="sage")
        self.memory = SwarmMemoryEntry.objects.create(title="m", content="c")
        self.codex = SwarmCodex.objects.create(
            title="Codex", created_by=self.assistant, symbolic_domain="myth"
        )

    def test_ritual_goal_planner(self):
        planner = RitualGoalPlanner.objects.create(
            assistant=self.assistant,
            goal_title="Quest",
            input_intention="Seek artifact",
            ritual_path=[{"step": "one"}],
        )
        planner.linked_codices.add(self.codex)
        planner.milestone_memory.add(self.memory)
        self.assertEqual(planner.assistant, self.assistant)
        self.assertEqual(planner.linked_codices.count(), 1)
        self.assertEqual(planner.milestone_memory.count(), 1)

    def test_myth_timeline_director(self):
        director = MythTimelineDirector.objects.create(
            title="Arc",
            assistant=self.assistant,
            timeline_segments=[{"phase": 1}],
            codex_weights={"c1": 0.5},
        )
        director.memory_nodes.add(self.memory)
        self.assertEqual(director.memory_nodes.count(), 1)
        self.assertEqual(director.assistant, self.assistant)

    def test_codex_decision_framework(self):
        framework = CodexDecisionFramework.objects.create(
            assistant=self.assistant,
            decision_context="context",
            codex_applied=self.codex,
            outcome_paths=[{"path": "A"}],
            symbolic_alignment_score=0.8,
        )
        self.assertEqual(framework.codex_applied, self.codex)
        self.assertAlmostEqual(framework.symbolic_alignment_score, 0.8)
