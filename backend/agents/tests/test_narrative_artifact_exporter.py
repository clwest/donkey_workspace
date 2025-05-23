import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from django.test import TestCase
from django.core.exceptions import ValidationError
from assistants.models import Assistant
from agents.models import SwarmMemoryEntry, LegacyArtifact, NarrativeArtifactExporter


class NarrativeArtifactExporterTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="A")
        self.mem = SwarmMemoryEntry.objects.create(title="t", content="c")
        self.artifact = LegacyArtifact.objects.create(
            assistant=self.assistant,
            artifact_type="scroll",
            source_memory=self.mem,
            symbolic_tags={},
        )

    def test_valid_format(self):
        exporter = NarrativeArtifactExporter(
            artifact=self.artifact,
            assistant=self.assistant,
            export_format="json",
        )
        exporter.full_clean()
        exporter.save()
        self.assertEqual(exporter.export_format, "json")

    def test_invalid_format(self):
        exporter = NarrativeArtifactExporter(
            artifact=self.artifact,
            assistant=self.assistant,
            export_format="txt",
        )
        with self.assertRaises(ValidationError):
            exporter.full_clean()
