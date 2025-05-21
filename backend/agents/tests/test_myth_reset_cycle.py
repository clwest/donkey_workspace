import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase

from agents.utils.myth_reset import run_myth_reset_cycle
from agents.models import SwarmMemoryEntry


class MythResetCycleTest(TestCase):
    def test_run_cycle_creates_memory(self):
        result = run_myth_reset_cycle()
        self.assertIn("memory_entry", result)
        self.assertTrue(
            SwarmMemoryEntry.objects.filter(id=result["memory_entry"]).exists()
        )
