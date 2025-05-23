import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from agents.models import (
    MythicIdentityCard,
    CrossTimelineReflectionRite,
    ArchetypeFusionEvent,
)


class Phase73ModelTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="A")
        self.card = MythicIdentityCard.objects.create(
            assistant=self.assistant,
            identity_signature="sig",
            symbolic_traits={},
            narrative_roles={},
            lineage_map={},
        )

    def test_identity_card(self):
        self.assertEqual(self.card.assistant, self.assistant)

    def test_reflection_rite(self):
        rite = CrossTimelineReflectionRite.objects.create(
            assistant=self.assistant,
            ritual_summary="sum",
            symbolic_convergence_score=0.5,
        )
        rite.reflected_identities.add(self.card)
        self.assertEqual(rite.reflected_identities.count(), 1)

    def test_archetype_fusion_event(self):
        event = ArchetypeFusionEvent.objects.create(
            primary_archetype="sage",
            merged_with="warrior",
            resulting_archetype="sage-warrior",
            symbolic_justification="balance",
            fusion_initiator=self.assistant,
        )
        self.assertEqual(event.resulting_archetype, "sage-warrior")
