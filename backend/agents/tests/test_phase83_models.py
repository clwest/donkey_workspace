import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant, AssistantGuild
from agents.models import (
    SwarmMemoryEntry,
    TranscendentMyth,
    MemoryRealmZone,
    RitualSyncPulse,
    ArchetypeFieldCluster,
)


class Phase83ModelTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="A")
        self.assistant2 = Assistant.objects.create(name="B")
        self.guild = AssistantGuild.objects.create(name="G")
        self.memory = SwarmMemoryEntry.objects.create(title="m", content="c")
        self.myth = TranscendentMyth.objects.create(name="Myth")

    def test_memory_realm_zone(self):
        zone = MemoryRealmZone.objects.create(
            zone_name="Zone",
            origin_myth=self.myth,
            spatial_traits={},
            symbolic_navigation_tags={},
        )
        zone.memory_inhabitants.add(self.memory)
        self.assertEqual(zone.origin_myth, self.myth)
        self.assertIn(self.memory, zone.memory_inhabitants.all())

    def test_ritual_sync_pulse(self):
        pulse = RitualSyncPulse.objects.create(
            pulse_id="p1",
            initiating_guild=self.guild,
            sync_tags={},
            phase_trigger="solstice",
        )
        pulse.synchronization_targets.add(self.assistant, self.assistant2)
        self.assertEqual(pulse.initiating_guild, self.guild)
        self.assertEqual(pulse.synchronization_targets.count(), 2)

    def test_archetype_field_cluster(self):
        cluster = ArchetypeFieldCluster.objects.create(
            cluster_name="C",
            anchor_roles={},
            resonance_score=0.5,
            symbolic_purpose_vector={},
        )
        cluster.participating_assistants.add(self.assistant)
        self.assertIn(self.assistant, cluster.participating_assistants.all())
