from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
from intel_core.models import Document, DocumentChunk
from memory.models import MemoryEntry
from embeddings.models import Embedding


class Command(BaseCommand):
    help = "Repair Document→Assistant→Context links and embedding references"

    def handle(self, *args, **options):
        doc_fixed = 0
        for doc in Document.objects.filter(memory_context__isnull=True).prefetch_related("linked_assistants", "assigned_assistants"):
            a = doc.linked_assistants.first() or doc.assigned_assistants.first()
            if a and a.memory_context:
                doc.memory_context = a.memory_context
                doc.save(update_fields=["memory_context"])
                doc_fixed += 1
        self.stdout.write(self.style.SUCCESS(f"Updated {doc_fixed} documents"))

        ct_chunk = ContentType.objects.get_for_model(DocumentChunk)
        chunk_fixed = 0
        for chunk in DocumentChunk.objects.select_related("embedding"):
            emb = chunk.embedding
            if not emb:
                continue
            changed = False
            if emb.content_id != str(chunk.id):
                emb.content_id = str(chunk.id)
                changed = True
            if emb.content_type != ct_chunk:
                emb.content_type = ct_chunk
                changed = True
            if emb.content and emb.content.startswith("namespace("):
                emb.content = chunk.text
                changed = True
            if changed:
                emb.save(update_fields=["content_type", "content_id", "content"])
                chunk_fixed += 1
        self.stdout.write(self.style.SUCCESS(f"Fixed {chunk_fixed} chunk embeddings"))

        ct_mem = ContentType.objects.get_for_model(MemoryEntry)
        mem_fixed = 0
        for mem in MemoryEntry.objects.filter(embeddings__isnull=False).prefetch_related("embeddings"):
            for emb in mem.embeddings.all():
                changed = False
                if emb.content_id != str(mem.id):
                    emb.content_id = str(mem.id)
                    changed = True
                if emb.content_type != ct_mem:
                    emb.content_type = ct_mem
                    changed = True
                if changed:
                    emb.save(update_fields=["content_type", "content_id"])
                    mem_fixed += 1
        self.stdout.write(self.style.SUCCESS(f"Fixed {mem_fixed} memory embeddings"))
