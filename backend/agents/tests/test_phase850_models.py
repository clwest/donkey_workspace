import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from agents.models import (
    SwarmMemoryEntry,
    SymbolicStrategyChamber,
    PurposeConflictResolutionLog,
    RitualVotingEvent,
)


class Phase850ModelTest(TestCase):
    def setUp(self):
        self.a1 = Assistant.objects.create(name="A")
        self.a2 = Assistant.objects.create(name="B")
        self.mem = SwarmMemoryEntry.objects.create(title="m", content="c")

    def test_strategy_chamber(self):
        chamber = SymbolicStrategyChamber.objects.create(
            chamber_title="C",
            strategy_context="ctx",
            decision_threads=[],
            symbolic_focus_tags=[],
        )
        chamber.participants.add(self.a1, self.a2)
        self.assertEqual(chamber.participants.count(), 2)

    def test_conflict_resolution_log(self):
        log = PurposeConflictResolutionLog.objects.create(
            conflict_topic="t",
            resolution_method="ritual",
            symbolic_outcome="ok",
        )
        log.assistants_involved.add(self.a1)
        log.memory_basis.add(self.mem)
        self.assertEqual(log.assistants_involved.count(), 1)
        self.assertEqual(log.memory_basis.count(), 1)

    def test_ritual_voting_event(self):
        event = RitualVotingEvent.objects.create(
            event_title="v",
            mythic_question="why",
            candidate_outcomes={"a": 1},
            vote_result="yes",
        )
        event.voter_pool.add(self.a1)
        self.assertEqual(event.voter_pool.count(), 1)
