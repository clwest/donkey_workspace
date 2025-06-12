from django.core.management.base import BaseCommand
from embeddings.models import Embedding
from intel_core.models import DocumentChunk
import re

class Command(BaseCommand):
    help = "Repair Embedding.content for document chunks"

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=None)

    def handle(self, *args, **options):
        limit = options.get("limit")
        qs = Embedding.objects.filter(
            content__startswith="namespace(content_type='document_chunk"
        ).order_by("id")
        if limit:
            qs = qs[:limit]
        pattern = re.compile(r"id='([^']+)'")
        fixed = 0
        for emb in qs:
            chunk_id = emb.object_id or emb.content_id
            match = pattern.search(emb.content or "")
            if match:
                chunk_id = match.group(1)
            chunk = DocumentChunk.objects.filter(id=chunk_id).first()
            if chunk and chunk.text:
                emb.content = chunk.text
                emb.save(update_fields=["content"])
                fixed += 1
        self.stdout.write(f"Fixed {fixed} embeddings")
