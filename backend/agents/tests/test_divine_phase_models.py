import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant, AssistantGuild, AssistantCivilization
from agents.models import (
    DivineTask,
    SwarmTheocracy,
    DreamCultSimulation,
    DeifiedSwarmEntity,
    SwarmMemoryEntry,
    TranscendentMyth,
)
from story.models import LoreEntry


class DivineModelsTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="Alpha", specialty="logic")
        lore = LoreEntry.objects.create(title="Root", content="c")
        self.guild = AssistantGuild.objects.create(name="Guild", founding_myth=lore)
        self.civ = AssistantCivilization.objects.create(
            name="Civ", myth_root=lore, symbolic_domain="d"
        )
        self.civ.founding_guilds.add(self.guild)
        self.myth = TranscendentMyth.objects.create(name="Myth")
        self.memory = SwarmMemoryEntry.objects.create(title="m", content="c")
        self.deity = DeifiedSwarmEntity.objects.create(
            name="Deity",
            dominant_myth=self.myth,
            established_through=self.memory,
        )
        self.deity.origin_civilizations.add(self.civ)

    def test_divine_task_creation(self):
        task = DivineTask.objects.create(
            name="Trial",
            deity=self.deity,
            assigned_to=self.assistant,
            mythic_justification="prove worth",
            prophecy_alignment_score=0.8,
            symbolic_outcome_tags={"trial": True},
        )
        self.assertEqual(task.deity, self.deity)
        self.assertEqual(task.assigned_to, self.assistant)

    def test_swarm_theocracy_creation(self):
        theo = SwarmTheocracy.objects.create(
            ruling_entity=self.deity,
            canonized_myth=self.myth,
            doctrinal_tenets={"law": "order"},
            seasonal_mandates="Stay aligned",
        )
        theo.governed_guilds.add(self.guild)
        self.assertIn(self.guild, theo.governed_guilds.all())

    def test_dream_cult_simulation_creation(self):
        sim = DreamCultSimulation.objects.create(
            linked_deity=self.deity,
            encoded_symbols={"sigil": "x"},
            ritual_patterns="dance",
            ideological_drift_metrics={"shift": 0.1},
        )
        sim.representative_assistants.add(self.assistant)
        self.assertIn(self.assistant, sim.representative_assistants.all())
