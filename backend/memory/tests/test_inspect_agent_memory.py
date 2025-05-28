import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from io import StringIO
from django.core.management import call_command
from django.test import TestCase
from agents.models import Agent
from intel_core.models import Document, DocumentChunk
from memory.models import SymbolicMemoryAnchor


class InspectAgentMemoryCommandTest(TestCase):
    def setUp(self):
        self.agent = Agent.objects.create(name="Zeno", slug="zeno-the-owl")
        self.doc = Document.objects.create(title="LangChain Guide", content="t")
        self.agent.trained_documents.add(self.doc)
        self.anchor = SymbolicMemoryAnchor.objects.create(slug="zk-rollup", label="ZK-Rollup")
        DocumentChunk.objects.create(
            document=self.doc,
            order=1,
            text="zk rollup explanation",
            tokens=5,
            fingerprint="abc",
            score=0.8,
            anchor=self.anchor,
            is_glossary=True,
        )

    def test_command_outputs_chunk(self):
        out = StringIO()
        call_command(
            "inspect_agent_memory",
            "--agent",
            self.agent.slug,
            "--slug",
            self.anchor.slug,
            stdout=out,
        )
        output = out.getvalue()
        self.assertIn(self.agent.slug, output)
        self.assertIn(self.anchor.slug, output)
        self.assertIn("LangChain Guide", output)
