import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from agents.models import (
    SwarmMemoryEntry,
    SwarmCodex,
    EncodedRitualBlueprint,
    StoryConvergencePath,
    RitualFusionEvent,
    NarrativeCurationTimeline,
)


class Phase128ModelsTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="A")
        self.memory = SwarmMemoryEntry.objects.create(title="M", content="c")
        self.codex = SwarmCodex.objects.create(
            title="C", created_by=self.assistant, symbolic_domain="myth"
        )
        self.blueprint = EncodedRitualBlueprint.objects.create(
            name="R", encoded_steps=[]
        )

    def test_story_convergence_path(self):
        path = StoryConvergencePath.objects.create(
            initiating_assistant=self.assistant,
            symbolic_unity_vector={},
            convergence_summary="sum",
        )
        path.involved_memory.add(self.memory)
        path.codex_targets.add(self.codex)
        self.assertEqual(path.initiating_assistant, self.assistant)
        self.assertEqual(path.codex_targets.count(), 1)

    def test_ritual_fusion_event(self):
        event = RitualFusionEvent.objects.create(
            initiator_id="u1",
            fusion_script={},
            symbolic_impact_summary="impact",
            codex_context=self.codex,
        )
        event.ritual_components.add(self.blueprint)
        self.assertEqual(event.codex_context, self.codex)
        self.assertEqual(event.ritual_components.count(), 1)

    def test_narrative_curation_timeline(self):
        timeline = NarrativeCurationTimeline.objects.create(
            title="T",
            contributors={"a": 1},
            timeline_segments=[],
        )
        timeline.linked_memory.add(self.memory)
        timeline.codex_nodes.add(self.codex)
        self.assertEqual(timeline.title, "T")
        self.assertEqual(timeline.codex_nodes.count(), 1)
