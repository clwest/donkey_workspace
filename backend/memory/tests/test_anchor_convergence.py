import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.test_settings")
import django

django.setup()

from django.test import TestCase
from unittest.mock import patch

from assistants.models import Assistant
from memory.models import SymbolicMemoryAnchor, AnchorConvergenceLog
from utils import llm_router


class AnchorConvergenceLogTests(TestCase):
    @patch("assistants.utils.chunk_retriever.get_relevant_chunks")
    @patch("assistants.utils.memory_summoner.summon_relevant_memories")
    @patch("utils.llm_router.call_llm")
    def test_convergence_log_created(self, mock_llm, mock_summon, mock_chunks):
        assistant = Assistant.objects.create(name="A", specialty="s")
        anchor = SymbolicMemoryAnchor.objects.create(slug="zk-rollup", label="ZK Rollup")

        mock_summon.return_value = ("", [])
        mock_chunks.return_value = (
            [
                {
                    "chunk_id": "1",
                    "document_id": "d1",
                    "score": 0.9,
                    "text": "zk rollup definition",
                    "source_doc": "doc",
                    "is_glossary": True,
                    "anchor_slug": "zk-rollup",
                    "anchor_confidence": 1.0,
                    "fingerprint": "f1",
                    "anchor_boost": 0.1,
                }
            ],
            None,
            False,
            True,
            0.9,
            "1",
            False,
            False,
            [],
        )
        mock_llm.return_value = "zk rollup explanation"

        reply, _, meta = llm_router.chat(
            [{"role": "user", "content": "what is zk rollup"}],
            assistant,
            enable_retry_logging=True,
        )
        self.assertEqual(reply, "zk rollup explanation")
        log = AnchorConvergenceLog.objects.first()
        self.assertIsNotNone(log)
        self.assertEqual(log.anchor, anchor)
        self.assertEqual(log.assistant, assistant)
        self.assertFalse(log.retried)
        self.assertTrue(meta.get("convergence_log_id"))

    @patch("assistants.utils.chunk_retriever.get_relevant_chunks")
    @patch("assistants.utils.memory_summoner.summon_relevant_memories")
    @patch("utils.llm_router.call_llm")
    def test_convergence_log_filtered_by_assistant(self, mock_llm, mock_summon, mock_chunks):
        a1 = Assistant.objects.create(name="A1", specialty="s")
        a2 = Assistant.objects.create(name="A2", specialty="s")
        anchor = SymbolicMemoryAnchor.objects.create(slug="zk-rollup", label="ZK Rollup")

        mock_summon.return_value = ("", [])
        mock_chunks.return_value = (
            [
                {
                    "chunk_id": "1",
                    "document_id": "d1",
                    "score": 0.9,
                    "text": "zk rollup definition",
                    "source_doc": "doc",
                    "is_glossary": True,
                    "anchor_slug": "zk-rollup",
                    "anchor_confidence": 1.0,
                    "fingerprint": "f1",
                    "anchor_boost": 0.1,
                }
            ],
            None,
            False,
            True,
            0.9,
            "1",
            False,
            False,
            [],
        )
        mock_llm.return_value = "zk rollup explanation"

        llm_router.chat([{"role": "user", "content": "what is zk rollup"}], a1, enable_retry_logging=True)
        llm_router.chat([{"role": "user", "content": "what is zk rollup"}], a2, enable_retry_logging=True)

        resp = self.client.get(
            f"/api/memory/symbolic-anchors/{anchor.slug}/convergence/?assistant={a1.id}"
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["results"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["assistant"], str(a1.id))

    @patch("assistants.utils.chunk_retriever.get_relevant_chunks")
    @patch("assistants.utils.memory_summoner.summon_relevant_memories")
    @patch("utils.llm_router.call_llm")
    def test_assistant_convergence_endpoint(self, mock_llm, mock_summon, mock_chunks):
        assistant = Assistant.objects.create(name="A", specialty="s")
        anchor = SymbolicMemoryAnchor.objects.create(slug="zk-rollup", label="ZK Rollup")

        mock_summon.return_value = ("", [])
        mock_chunks.return_value = (
            [
                {
                    "chunk_id": "1",
                    "document_id": "d1",
                    "score": 0.9,
                    "text": "zk rollup definition",
                    "source_doc": "doc",
                    "is_glossary": True,
                    "anchor_slug": "zk-rollup",
                    "anchor_confidence": 1.0,
                    "fingerprint": "f1",
                    "anchor_boost": 0.1,
                }
            ],
            None,
            False,
            True,
            0.9,
            "1",
            False,
            False,
            [],
        )
        mock_llm.return_value = "zk rollup explanation"

        llm_router.chat([{"role": "user", "content": "what is zk rollup"}], assistant, enable_retry_logging=True)

        resp = self.client.get(f"/api/memory/symbolic-anchors/convergence/?assistant={assistant.id}")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["results"]
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["assistant"], str(assistant.id))

