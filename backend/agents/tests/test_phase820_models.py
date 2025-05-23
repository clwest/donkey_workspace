import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from agents.models import (
    SignalEncodingArtifact,
    BeliefNavigationVector,
    ReflectiveFluxIndex,
)


class Phase820ModelTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="A")

    def test_signal_encoding_artifact(self):
        art = SignalEncodingArtifact.objects.create(
            source=self.assistant,
            encoding_payload="abc",
            symbolic_origin="myth",
            modulation_tags={"key": "val"},
            receiver_scope="all",
        )
        self.assertEqual(art.source, self.assistant)
        self.assertEqual(art.receiver_scope, "all")

    def test_belief_navigation_vector(self):
        vec = BeliefNavigationVector.objects.create(
            assistant=self.assistant,
            vector_path=["start", "end"],
            alignment_score=0.5,
        )
        self.assertEqual(vec.assistant, self.assistant)
        self.assertEqual(vec.vector_path[0], "start")

    def test_reflective_flux_index(self):
        idx = ReflectiveFluxIndex.objects.create(
            swarm_scope="global",
            flux_measurements={"entropy": 0.1},
            insight_summary="ok",
        )
        self.assertEqual(idx.swarm_scope, "global")
