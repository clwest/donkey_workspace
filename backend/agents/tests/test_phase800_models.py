import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from agents.models import (
    AscensionStructure,
    MythicMemoryPalace,
    EternalReturnCycleIndex,
    TranscendentMyth,
    SwarmMemoryEntry,
)


class Phase800ModelTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="A1")
        self.myth = TranscendentMyth.objects.create(name="M")
        self.memory = SwarmMemoryEntry.objects.create(title="t", content="c")

    def test_ascension_structure(self):
        struct = AscensionStructure.objects.create(
            name="S", symbolic_requirements={"x": 1}
        )
        struct.core_myths.add(self.myth)
        struct.qualifying_assistants.add(self.assistant)
        self.assertEqual(struct.core_myths.count(), 1)
        self.assertEqual(struct.qualifying_assistants.count(), 1)

    def test_mythic_memory_palace(self):
        palace = MythicMemoryPalace.objects.create(
            assistant=self.assistant,
            palace_structure={},
            symbolic_keys={},
            purpose_alignment_summary="p",
        )
        self.assertEqual(palace.assistant, self.assistant)

    def test_eternal_return_cycle_index(self):
        cycle = EternalReturnCycleIndex.objects.create(
            cycle_name="C",
            symbolic_theme_tags={},
            closed_loop_reflection="r",
        )
        cycle.reincarnation_nodes.add(self.assistant)
        cycle.indexed_memories.add(self.memory)
        self.assertEqual(cycle.reincarnation_nodes.count(), 1)
        self.assertEqual(cycle.indexed_memories.count(), 1)
