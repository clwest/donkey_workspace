import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from agents.models import (
    BeliefForkEvent,
    MythCollapseLog,
    MemoryReformationRitual,
    TranscendentMyth,
    SwarmMemoryEntry,
    LoreToken,
)
from memory.models import MemoryBranch


class Phase493ModelTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="Alpha")
        self.memory = SwarmMemoryEntry.objects.create(title="m", content="c")
        self.myth = TranscendentMyth.objects.create(name="Myth")
        self.branch = MemoryBranch.objects.create(
            root_entry=self.memory, fork_reason="t", speculative_outcome="o"
        )

    def test_belief_fork_event(self):
        event = BeliefForkEvent.objects.create(
            originating_assistant=self.assistant,
            parent_belief_vector={"a": 1},
            forked_belief_vector={"a": 0},
            reason="diverge",
        )
        event.resulting_assistants.add(self.assistant)
        self.assertEqual(event.originating_assistant, self.assistant)
        self.assertEqual(event.resulting_assistants.count(), 1)

    def test_myth_collapse_log(self):
        token = LoreToken.objects.create(name="T")
        log = MythCollapseLog.objects.create(
            myth=self.myth,
            trigger_event=self.memory,
            collapse_reason="lost",
        )
        log.fragments_preserved.add(token)
        self.assertEqual(log.myth, self.myth)
        self.assertEqual(log.fragments_preserved.count(), 1)

    def test_memory_reformation_ritual(self):
        ritual = MemoryReformationRitual.objects.create(
            initiating_assistant=self.assistant,
            symbolic_intent="restore",
            reformed_summary="s",
            new_memory_thread=self.branch,
        )
        ritual.fragmented_memories.add(self.memory)
        self.assertEqual(ritual.new_memory_thread, self.branch)
        self.assertEqual(ritual.fragmented_memories.count(), 1)
