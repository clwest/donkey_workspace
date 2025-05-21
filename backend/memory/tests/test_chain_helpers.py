import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from unittest.mock import patch
from memory.models import MemoryEntry, MemoryChain
from memory.utils.chain_helpers import summarize_memory_chain, generate_flowmap_from_chain


class ChainHelperTests(TestCase):
    def setUp(self):
        self.entries = [MemoryEntry.objects.create(event=f"m{i}") for i in range(35)]
        self.chain = MemoryChain.objects.create(title="chain")
        self.chain.memories.set(self.entries)

    @patch("memory.utils.chain_helpers.call_gpt4")
    def test_summarize_memory_chain_limit(self, mock_call):
        mock_call.return_value = "ok"
        summary = summarize_memory_chain(self.chain)
        self.assertEqual(summary, "ok")
        self.chain.refresh_from_db()
        self.assertEqual(self.chain.summary, "ok")
        prompt = mock_call.call_args[0][0]
        self.assertNotIn("m30", prompt)
        self.assertIn("m0", prompt)

    def test_generate_flowmap_structure(self):
        data = generate_flowmap_from_chain(self.chain)
        self.assertIn("nodes", data)
        self.assertIn("edges", data)
        self.assertEqual(len(data["nodes"]), len(self.entries))
        self.assertEqual(len(data["edges"]), len(self.entries) - 1)
        first_edge = data["edges"][0]
        self.assertEqual(first_edge["source"], str(self.entries[0].id))
