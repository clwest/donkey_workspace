import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.test_settings")
import django

django.setup()

from django.test import TestCase
from memory.models import SymbolicMemoryAnchor
from memory.services.acquisition import update_anchor_acquisition
from assistants.models import Assistant


class AnchorAcquisitionTests(TestCase):
    def test_stage_progression(self):
        assistant = Assistant.objects.create(name="A", specialty="s")
        anchor = SymbolicMemoryAnchor.objects.create(slug="term", label="Term", assistant=assistant)
        self.assertEqual(anchor.acquisition_stage, "unseen")

        update_anchor_acquisition(anchor, "exposed")
        anchor.refresh_from_db()
        self.assertEqual(anchor.acquisition_stage, "exposed")
        assistant.refresh_from_db()
        self.assertEqual(assistant.glossary_score, 0)

        update_anchor_acquisition(anchor, "acquired")
        anchor.refresh_from_db()
        self.assertEqual(anchor.acquisition_stage, "acquired")
        assistant.refresh_from_db()
        self.assertEqual(assistant.glossary_score, 1)

        # downgrade attempt should have no effect
        update_anchor_acquisition(anchor, "exposed")
        anchor.refresh_from_db()
        self.assertEqual(anchor.acquisition_stage, "acquired")

        update_anchor_acquisition(anchor, "reinforced")
        anchor.refresh_from_db()
        self.assertEqual(anchor.acquisition_stage, "reinforced")
        assistant.refresh_from_db()
        self.assertEqual(assistant.glossary_score, 1)
