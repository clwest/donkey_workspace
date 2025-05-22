import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant, AssistantGuild
from agents.models import (
    AssistantPolity,
    RitualElection,
    LegacyRoleBinding,
    SwarmCodex,
    SwarmMemoryEntry,
)


class Phase500ModelTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="A")
        self.guild = AssistantGuild.objects.create(name="G")
        self.codex = SwarmCodex.objects.create(
            title="C", created_by=self.assistant, symbolic_domain="myth"
        )
        self.memory = SwarmMemoryEntry.objects.create(title="t", content="c")

    def test_assistant_polity(self):
        polity = AssistantPolity.objects.create(
            name="P",
            founding_codex=self.codex,
            core_purpose_statement="p",
        )
        polity.member_guilds.add(self.guild)
        polity.leadership_assistants.add(self.assistant)
        self.assertEqual(polity.member_guilds.count(), 1)
        self.assertEqual(polity.leadership_assistants.count(), 1)

    def test_ritual_election(self):
        polity = AssistantPolity.objects.create(
            name="P2",
            founding_codex=self.codex,
            core_purpose_statement="p",
        )
        election = RitualElection.objects.create(
            polity=polity,
            election_type="ascension",
            ballot_memory=self.memory,
        )
        election.candidates.add(self.assistant)
        self.assertEqual(election.candidates.count(), 1)
        self.assertEqual(election.ballot_memory, self.memory)

    def test_legacy_role_binding(self):
        role = LegacyRoleBinding.objects.create(
            role_name="Herald",
            assigned_to=self.assistant,
            bonded_memory=self.memory,
            origin_polity=None,
            renewal_conditions="yearly",
        )
        self.assertEqual(role.assigned_to, self.assistant)
        self.assertEqual(role.status, "active")
