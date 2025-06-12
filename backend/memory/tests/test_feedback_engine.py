import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.test_settings")
import django

django.setup()

from django.test import TestCase
from unittest.mock import patch

from assistants.models import Assistant
from assistants.models.reflection import AssistantReflectionLog
from memory.models import MemoryEntry, MemoryFeedback
from memory.utils.feedback_engine import apply_memory_feedback


class FeedbackEngineTests(TestCase):
    @patch("prompts.utils.mutation.call_llm", return_value="mutated summary")
    @patch("embeddings.helpers.helpers_io.get_embedding_for_text", return_value=[0.1])
    @patch("embeddings.helpers.helpers_io.save_embedding")
    @patch("memory.memory_service.auto_tag_from_embedding", return_value=[])
    def test_apply_positive_feedback_creates_new_entry(
        self, mock_auto_tag, mock_save, mock_embed, mock_llm
    ):
        assistant = Assistant.objects.create(name="A", specialty="s")
        mem = MemoryEntry.objects.create(
            event="e1",
            summary="original summary",
            assistant=assistant,
        )
        fb = MemoryFeedback.objects.create(
            memory=mem,
            suggestion="please shorten",
            mutation_style="shorten",
        )

        new_mem = apply_memory_feedback(fb)

        self.assertNotEqual(new_mem.id, mem.id)
        self.assertEqual(new_mem.parent_memory, mem)
        self.assertEqual(new_mem.summary, "mutated summary")
        self.assertEqual(AssistantReflectionLog.objects.count(), 1)

    @patch("prompts.utils.mutation.call_llm", return_value="clarified")
    @patch("embeddings.helpers.helpers_io.get_embedding_for_text", return_value=[0.1])
    @patch("embeddings.helpers.helpers_io.save_embedding")
    @patch("memory.memory_service.auto_tag_from_embedding", return_value=[])
    def test_apply_negative_feedback_updates_summary(
        self, mock_auto_tag, mock_save, mock_embed, mock_llm
    ):
        assistant = Assistant.objects.create(name="B", specialty="s")
        mem = MemoryEntry.objects.create(event="e2", assistant=assistant)
        fb = MemoryFeedback.objects.create(memory=mem, suggestion="clarify")

        updated_mem = apply_memory_feedback(fb)

        mem.refresh_from_db()
        self.assertEqual(updated_mem.id, mem.id)
        self.assertEqual(mem.summary, "clarified")
        self.assertEqual(AssistantReflectionLog.objects.count(), 1)
