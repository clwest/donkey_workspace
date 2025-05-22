
from django.test import TestCase
from unittest.mock import patch
from django.contrib.contenttypes.models import ContentType

from assistants.models import Assistant, AssistantThoughtLog
from memory.models import MemoryEntry
from embeddings.models import Embedding, EMBEDDING_LENGTH
from assistants.utils.memory_summoner import summon_relevant_memories


class MemorySummonTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="Summoner", specialty="m")
        self.mem1 = MemoryEntry.objects.create(
            event="alpha memory", assistant=self.assistant, summary="alpha"
        )
        self.mem2 = MemoryEntry.objects.create(
            event="beta memory", assistant=self.assistant, summary="beta"
        )
        ct = ContentType.objects.get_for_model(MemoryEntry)
        Embedding.objects.create(
            content_type=ct,
            object_id=self.mem1.id,
            content="alpha",
            embedding=[1.0] * EMBEDDING_LENGTH,
        )
        Embedding.objects.create(
            content_type=ct,
            object_id=self.mem2.id,
            content="beta",
            embedding=[0.0] * EMBEDDING_LENGTH,
        )

    @patch("assistants.utils.memory_summoner.get_embedding_for_text")
    def test_summon_relevant_memories(self, mock_get):
        mock_get.return_value = [1.0] * EMBEDDING_LENGTH
        text, ids = summon_relevant_memories("alpha question", self.assistant)
        self.assertIn("Recalled Memories", text)
        self.assertIn("alpha", text)
        self.assertEqual(ids, [str(self.mem1.id)])


class ChatMemorySummonTest(TestCase):
    @patch("assistants.utils.memory_summoner.get_embedding_for_text")
    @patch("utils.llm_router.call_llm")
    def test_chat_logs_ids(self, mock_call, mock_get):
        mock_get.return_value = [1.0] * EMBEDDING_LENGTH
        mock_call.return_value = "ok"
        assistant = Assistant.objects.create(
            name="Chatter", specialty="c", memory_summon_enabled=True
        )
        mem = MemoryEntry.objects.create(
            event="something", assistant=assistant, summary="thing"
        )
        ct = ContentType.objects.get_for_model(MemoryEntry)
        Embedding.objects.create(
            content_type=ct,
            object_id=mem.id,
            content="thing",
            embedding=[1.0] * EMBEDDING_LENGTH,
        )
        from rest_framework.test import APIClient

        client = APIClient()
        payload = {"message": "hi", "session_id": "s1"}
        resp = client.post(f"/api/assistants/{assistant.slug}/chat/", payload)
        self.assertEqual(resp.status_code, 200)
        log = AssistantThoughtLog.objects.filter(
            assistant=assistant, role="assistant"
        ).first()
        self.assertIn(str(mem.id), log.summoned_memory_ids)
