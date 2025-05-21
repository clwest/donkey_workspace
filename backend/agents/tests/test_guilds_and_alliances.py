import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from agents.models import AssistantGuild, SwarmAlliance, LoreEntry
from agents.utils import optimize_myth_architecture


class GuildAllianceTest(TestCase):
    def test_guild_and_alliance_creation(self):
        a1 = Assistant.objects.create(name="Alpha", specialty="logic")
        a2 = Assistant.objects.create(name="Beta", specialty="data")
        lore = LoreEntry.objects.create(title="Unity", summary="shared")
        guild = AssistantGuild.objects.create(name="Logic Guild", charter="R", myth_alignment=lore)
        guild.members.add(a1, a2)
        alliance = SwarmAlliance.objects.create(name="United", purpose="coop", terms={})
        alliance.founding_guilds.add(guild)
        self.assertEqual(guild.members.count(), 2)
        self.assertEqual(alliance.founding_guilds.count(), 1)

    def test_optimize_myth_architecture_keys(self):
        LoreEntry.objects.create(title="Symbol A", summary="x")
        report = optimize_myth_architecture()
        for key in [
            "deprecated_symbols",
            "overused_metaphors",
            "conflicting_myth_roots",
            "archetype_drift_patterns",
            "suggested_lore_merges",
        ]:
            self.assertIn(key, report)

