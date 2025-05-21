import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase

from assistants.models import Assistant, AssistantGuild, AssistantCivilization
from story.models import LoreEntry


class AssistantCivilizationTest(TestCase):
    def setUp(self):
        self.lore = LoreEntry.objects.create(title="Root", content="x")
        self.assistant = Assistant.objects.create(name="A", specialty="x")
        self.guild = AssistantGuild.objects.create(name="G", founding_myth=self.lore)
        self.guild.members.add(self.assistant)

    def test_create_civilization(self):
        civ = AssistantCivilization.objects.create(
            name="Civ", myth_root=self.lore, symbolic_domain="dream"
        )
        civ.founding_guilds.add(self.guild)
        self.assertEqual(civ.legacy_score, 0.0)
