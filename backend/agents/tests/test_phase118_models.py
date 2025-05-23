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
    ArchetypeFieldCluster,
    NarrativeLightingEngine,
    CinematicUILayer,
    AssistantTutorialScript,
    RitualOnboardingFlow,
)


class Phase118ModelsTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="A")
        self.codex = SwarmCodex.objects.create(
            title="C", created_by=self.assistant, symbolic_domain="myth"
        )
        self.blueprint = EncodedRitualBlueprint.objects.create(name="R", encoded_steps=[])
        self.cluster = ArchetypeFieldCluster.objects.create(
            cluster_name="cl", anchor_roles={}, resonance_score=0.1, symbolic_purpose_vector={}
        )
        self.light = NarrativeLightingEngine.objects.create(engine_name="L", lighting_params={})

    def test_cinematic_ui_layer(self):
        layer = CinematicUILayer.objects.create(
            layer_name="Intro",
            scene_trigger="start",
            animation_details={},
            lighting_engine=self.light,
            associated_archetype_cluster=self.cluster,
        )
        self.assertEqual(layer.layer_name, "Intro")
        self.assertEqual(layer.lighting_engine, self.light)

    def test_assistant_tutorial_script(self):
        script = AssistantTutorialScript.objects.create(
            assistant=self.assistant,
            tutorial_title="T",
            walkthrough_steps=[],
            belief_tags=[],
            role_focus="guide",
        )
        self.assertEqual(script.assistant, self.assistant)

    def test_ritual_onboarding_flow(self):
        flow = RitualOnboardingFlow.objects.create(
            entry_name="E",
            initiating_archetype="novice",
            required_codex=self.codex,
            ritual_blueprint=self.blueprint,
            step_sequence=[],
        )
        self.assertEqual(flow.required_codex, self.codex)
