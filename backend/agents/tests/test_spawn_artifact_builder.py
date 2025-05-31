import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from agents.models import Agent, LegacyArtifact, SwarmMemoryEntry
from agents.utils.artifact_builder import build_agent_spawn_artifact


class SpawnArtifactBuilderTest(TestCase):
    def test_build_agent_spawn_artifact(self):
        assistant = Assistant.objects.create(name="Base")
        agent = Agent.objects.create(name="Child", parent_assistant=assistant)

        artifact = build_agent_spawn_artifact(agent, "research")

        self.assertEqual(artifact.assistant, assistant)
        self.assertEqual(artifact.artifact_type, "agent_spawn")
        self.assertEqual(artifact.symbolic_tags.get("skill"), "research")
        self.assertTrue(SwarmMemoryEntry.objects.filter(id=artifact.source_memory.id).exists())

