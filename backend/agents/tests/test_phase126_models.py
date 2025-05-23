import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from agents.models import (
    SwarmMemoryEntry,
    SwarmCodex,
    EncodedRitualBlueprint,
    MythRecordingSession,
    SymbolicDocumentationEntry,
    BeliefArtifactArchive,
)


class Phase126ModelsTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="A")
        self.memory = SwarmMemoryEntry.objects.create(title="m", content="c")
        self.codex = SwarmCodex.objects.create(
            title="C", created_by=self.assistant, symbolic_domain="myth"
        )
        self.blueprint = EncodedRitualBlueprint.objects.create(
            name="R", encoded_steps=[]
        )

    def test_myth_recording_session(self):
        session = MythRecordingSession.objects.create(
            recorder_id="u1",
            linked_assistant=self.assistant,
            symbolic_tags={"t": 1},
            story_notes="note",
        )
        session.memory_reference.add(self.memory)
        self.assertEqual(session.linked_assistant, self.assistant)
        self.assertIn(self.memory, session.memory_reference.all())

    def test_symbolic_documentation_entry(self):
        entry = SymbolicDocumentationEntry.objects.create(
            author_id="u1",
            codex_reference=self.codex,
            entry_title="E",
            symbolic_themes={},
            ritual_connection=self.blueprint,
            content_body="body",
        )
        self.assertEqual(entry.codex_reference, self.codex)
        self.assertEqual(entry.ritual_connection, self.blueprint)

    def test_belief_artifact_archive(self):
        artifact = BeliefArtifactArchive.objects.create(
            contributor_id="u1",
            artifact_type="scroll",
            artifact_title="A",
            symbolic_payload={},
        )
        artifact.related_codices.add(self.codex)
        artifact.archived_memory.add(self.memory)
        self.assertIn(self.codex, artifact.related_codices.all())
        self.assertIn(self.memory, artifact.archived_memory.all())
