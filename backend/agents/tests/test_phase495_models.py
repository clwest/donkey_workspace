import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from agents.models import (
    BeliefNegotiationSession,
    ParadoxResolutionAttempt,
    OntologicalAuditLog,
    CognitiveConstraintProfile,
)


class Phase495ModelTest(TestCase):
    def setUp(self):
        self.a1 = Assistant.objects.create(name="A1")
        self.a2 = Assistant.objects.create(name="A2")
        self.profile = CognitiveConstraintProfile.objects.create(
            assistant=self.a1,
            prohibited_symbols={"x": True},
            mandatory_perspective={"view": "v"},
            constraint_justification="j",
        )

    def test_belief_negotiation_session(self):
        session = BeliefNegotiationSession.objects.create(contested_symbols={"a": 1})
        session.participants.add(self.a1, self.a2)
        session.constraint_conflicts.add(self.profile)
        self.assertEqual(session.participants.count(), 2)
        self.assertEqual(session.constraint_conflicts.count(), 1)

    def test_paradox_resolution_attempt(self):
        session = BeliefNegotiationSession.objects.create(contested_symbols={})
        attempt = ParadoxResolutionAttempt.objects.create(
            related_session=session,
            attempted_by=self.a1,
            logic_strategy="L",
            symbolic_result="R",
            was_successful=True,
        )
        self.assertTrue(attempt.was_successful)
        self.assertEqual(attempt.related_session, session)

    def test_ontological_audit_log(self):
        audit = OntologicalAuditLog.objects.create(
            scope="swarm",
            belief_alignment_summary="s",
            paradox_rate=0.1,
            recommended_actions="act",
        )
        audit.conflicting_constraints.add(self.profile)
        self.assertEqual(audit.scope, "swarm")
        self.assertEqual(audit.conflicting_constraints.count(), 1)
