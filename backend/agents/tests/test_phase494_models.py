import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from agents.models import (
    EpistemologyNode,
    BeliefEntanglementLink,
    CognitiveConstraintProfile,
    LoreToken,
    SwarmMemoryEntry,
)


class Phase494ModelTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="Alpha")
        self.other = Assistant.objects.create(name="Beta")
        self.token = LoreToken.objects.create(name="T")
        self.memory = SwarmMemoryEntry.objects.create(title="m", content="c")

    def test_epistemology_node(self):
        node = EpistemologyNode.objects.create(
            topic="Test",
            summary="s",
            belief_alignment_vector={"x": 1},
        )
        node.derived_from.add(self.token)
        node.authorized_by.add(self.assistant)
        self.assertEqual(node.topic, "Test")
        self.assertEqual(node.derived_from.count(), 1)

    def test_belief_entanglement_link(self):
        node = EpistemologyNode.objects.create(
            topic="T",
            summary="s",
            belief_alignment_vector={},
        )
        link = BeliefEntanglementLink.objects.create(
            assistant_a=self.assistant,
            assistant_b=self.other,
            relationship_type="dependency",
            symbolic_notes="n",
        )
        link.shared_epistemes.add(node)
        self.assertEqual(link.assistant_a, self.assistant)
        self.assertEqual(link.shared_epistemes.count(), 1)

    def test_cognitive_constraint_profile(self):
        profile = CognitiveConstraintProfile.objects.create(
            assistant=self.assistant,
            prohibited_symbols={"z": True},
            mandatory_perspective={"view": "v"},
            constraint_justification="j",
        )
        profile.memory_blindspots.add(self.memory)
        self.assertEqual(profile.assistant, self.assistant)
        self.assertEqual(profile.memory_blindspots.count(), 1)

