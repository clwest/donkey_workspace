import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase

from assistants.models import Assistant
from agents.models import LegacyArtifact, ReincarnationLog, SwarmMemoryEntry
from agents.utils.reincarnation import reincarnate_assistant_from_artifact


class LegacyArtifactReincarnationTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="Old", specialty="x")
        self.memory = SwarmMemoryEntry.objects.create(title="m", content="c")
        self.artifact = LegacyArtifact.objects.create(
            assistant=self.assistant,
            artifact_type="scroll",
            source_memory=self.memory,
            symbolic_tags={"name": "Neo"},
        )

    def test_reincarnate_assistant_from_artifact(self):
        new_assistant = reincarnate_assistant_from_artifact(self.artifact)
        self.assertNotEqual(new_assistant.id, self.assistant.id)
        log = ReincarnationLog.objects.get(descendant=new_assistant)
        self.assertIn(self.artifact, log.inherited_artifacts.all())
        self.assertEqual(log.ancestor, self.assistant)
