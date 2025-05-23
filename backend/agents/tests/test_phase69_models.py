import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from agents.models.lore import (
    EncodedRitualBlueprint,
    RitualMasteryRecord,
    PilgrimageLog,
)
from agents.utils.reincarnation import initiate_reincarnation_flow


class Phase69ModelTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="Mythic", specialty="myth")
        self.ritual = EncodedRitualBlueprint.objects.create(
            name="TestRitual", blueprint_code="code"
        )

    def test_ritual_mastery_record(self):
        record = RitualMasteryRecord.objects.create(
            assistant=self.assistant,
            symbolic_rank="novice",
            mastery_traits={"courage": 1},
        )
        record.completed_rituals.add(self.ritual)
        self.assertEqual(record.completed_rituals.count(), 1)
        self.assertEqual(record.symbolic_rank, "novice")

    def test_pilgrimage_log(self):
        log = PilgrimageLog.objects.create(
            assistant=self.assistant,
            pilgrimage_title="Journey",
            steps=[{"loc": "A"}],
            transformation_notes="none",
        )
        self.assertFalse(log.completed)
        self.assertEqual(log.pilgrimage_title, "Journey")

    def test_initiate_reincarnation_flow(self):
        result = initiate_reincarnation_flow(self.assistant.id)
        self.assertEqual(result["assistant"], self.assistant.id)
        self.assertIn("blueprint", result)
