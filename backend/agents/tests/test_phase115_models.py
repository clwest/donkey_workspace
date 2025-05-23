import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from agents.models import SwarmMemoryEntry, MemoryEchoEffectMap


class Phase115ModelTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="A")
        self.memory = SwarmMemoryEntry.objects.create(title="t", content="c")

    def test_memory_echo_effect_map(self):
        effect = MemoryEchoEffectMap.objects.create(
            memory=self.memory,
            trigger_type="ritual",
            visual_effect="sparkle",
            entropy_strength=0.5,
            particle_mode="glow",
        )
        self.assertEqual(effect.memory, self.memory)
        self.assertEqual(effect.trigger_type, "ritual")

