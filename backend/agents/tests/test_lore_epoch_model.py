import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase

from agents.models import LoreEpoch, SwarmMemoryEntry


class LoreEpochModelTest(TestCase):
    def test_create_epoch(self):
        start = SwarmMemoryEntry.objects.create(title="s", content="start")
        end = SwarmMemoryEntry.objects.create(title="e", content="end")
        epoch = LoreEpoch.objects.create(
            title="Era One", summary="testing", start_event=start, end_event=end
        )
        self.assertEqual(epoch.title, "Era One")
        self.assertFalse(epoch.closed)
