import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from agents.models import (
    SwarmCosmology,
    PurposeIndexEntry,
    BeliefSignalNode,
    MythicAlignmentMarket,
)


class Phase62ModelTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="A")
        self.cosmology = SwarmCosmology.objects.create(name="Cosmos")

    def test_purpose_index_entry(self):
        entry = PurposeIndexEntry.objects.create(
            assistant=self.assistant,
            cosmology=self.cosmology,
            purpose_vector={"p": 1},
            timeline_marker="t1",
            alignment_tags={}
        )
        self.assertEqual(entry.assistant, self.assistant)
        self.assertEqual(entry.cosmology, self.cosmology)

    def test_belief_signal_node(self):
        node = BeliefSignalNode.objects.create(
            origin_assistant=self.assistant,
            transmitted_beliefs={},
            signal_strength=0.9,
            inheritance_type="core",
        )
        node.receivers.add(self.assistant)
        self.assertEqual(node.receivers.count(), 1)
        self.assertEqual(node.signal_strength, 0.9)

    def test_alignment_market(self):
        market = MythicAlignmentMarket.objects.create(
            participant=self.assistant,
            alignment_score=0.8,
            ritual_contributions={},
            symbolic_asset_tags={},
            access_level="basic",
        )
        self.assertEqual(market.participant, self.assistant)
        self.assertEqual(market.access_level, "basic")
