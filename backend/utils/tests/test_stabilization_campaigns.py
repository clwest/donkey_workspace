import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from metrics.models import CodexClauseVote
from agents.models.lore import SwarmMemoryEntry
from utils.stabilization_campaigns import launch_stabilization_campaign


class StabilizationCampaignTest(TestCase):
    def test_launch_creates_memory(self):
        CodexClauseVote.objects.create(
            clause_id="c1",
            suggested_mutation="m1",
            symbolic_tags=["tag"],
            vote_choice="approve",
        )
        CodexClauseVote.objects.create(
            clause_id="c1",
            suggested_mutation="m1",
            symbolic_tags=["tag"],
            vote_choice="reject",
        )

        entry_id = launch_stabilization_campaign("c1")
        self.assertTrue(SwarmMemoryEntry.objects.filter(id=entry_id).exists())
