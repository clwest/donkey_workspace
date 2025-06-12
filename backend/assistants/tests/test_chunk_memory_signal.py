from django.test import TestCase
from assistants.models import Assistant
from intel_core.models import Document, DocumentChunk
from memory.models import MemoryEntry
from django.contrib.contenttypes.models import ContentType
import uuid

class ChunkMemorySignalTest(TestCase):
    def test_chunk_memory_uses_assistant_context(self):
        assistant = Assistant.objects.create(name="SigBot", specialty="s")
        doc = Document.objects.create(title="D", content="c", source_type="text")
        doc.linked_assistants.add(assistant)
        chunk = DocumentChunk.objects.create(
            document=doc,
            order=0,
            text="hello",
            tokens=5,
            fingerprint=str(uuid.uuid4())
        )
        ct = ContentType.objects.get_for_model(DocumentChunk)
        mem = MemoryEntry.objects.filter(
            linked_content_type=ct,
            linked_object_id=chunk.id,
            assistant=assistant,
        ).first()
        self.assertIsNotNone(mem)
        self.assertEqual(mem.context, assistant.memory_context)

