import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from io import StringIO
from django.core.management import call_command
from django.test import TestCase
from agents.models import Agent
from assistants.models import Assistant
from intel_core.models import Document, DocumentChunk, EmbeddingMetadata
from memory.models import SymbolicMemoryAnchor


class InspectAgentMemoryCommandTest(TestCase):
    def setUp(self):
        self.agent = Agent.objects.create(name="Zeno", slug="zeno-the-owl")
        self.assistant = Assistant.objects.create(name="Rollup", slug="zk-rollup")
        self.doc = Document.objects.create(title="LangChain Guide", content="t")
        self.assistant.documents.add(self.doc)
        self.agent.trained_documents.add(self.doc)
        self.anchor = SymbolicMemoryAnchor.objects.create(slug="zk-rollup", label="ZK-Rollup")
        chunk = DocumentChunk.objects.create(
            document=self.doc,
            order=1,
            text="zk rollup explanation",
            tokens=5,
            fingerprint="abc",
            score=0.8,
            anchor=self.anchor,
            is_glossary=True,
        )
        emb = EmbeddingMetadata.objects.create(model_used="t", num_tokens=5, vector=[0.0])
        chunk.embedding = emb
        chunk.save()

    def test_command_outputs_chunk(self):
        out = StringIO()
        call_command(
            "inspect_agent_memory",
            "--assistant",
            self.assistant.slug,
            "--slug",
            self.anchor.slug,
            stdout=out,
        )
        output = out.getvalue()
        self.assertIn(self.assistant.slug, output)
        self.assertIn(self.anchor.slug, output)
        self.assertIn("LangChain Guide", output)
        self.assertIn("Used Chunks", output)

    def test_doc_suggestion(self):
        out = StringIO()
        call_command(
            "inspect_agent_memory",
            "--assistant",
            self.assistant.slug,
            "--doc",
            "foobar",
            stdout=out,
        )
        output = out.getvalue()
        self.assertIn("Did you mean", output)
