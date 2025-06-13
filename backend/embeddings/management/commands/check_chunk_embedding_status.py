from django.core.management.base import BaseCommand
from intel_core.models import DocumentChunk
from assistants.utils.resolve import resolve_assistant

class Command(BaseCommand):
    """Audit embedding status for document chunks."""

    help = "Check for missing or invalid embeddings on chunks"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", help="Assistant slug to filter", default=None)

    def handle(self, *args, **options):
        slug = options.get("assistant")
        if slug:
            assistant = resolve_assistant(slug)
            if not assistant:
                self.stderr.write(self.style.ERROR(f"Assistant '{slug}' not found"))
                return
            doc_ids = assistant.documents.values_list("id", flat=True)
            chunks = DocumentChunk.objects.filter(document_id__in=doc_ids)
        else:
            chunks = DocumentChunk.objects.all()

        total = chunks.count()
        missing = chunks.filter(embedding__isnull=True).count()
        invalid = 0
        for ch in chunks.select_related("embedding"):
            if ch.embedding and (not ch.embedding.vector or not any(ch.embedding.vector)):
                invalid += 1
                if ch.embedding_valid:
                    ch.embedding_valid = False
                    ch.save(update_fields=["embedding_valid"])
        glossary_zero = chunks.filter(is_glossary=True, glossary_score=0).count()

        self.stdout.write("\U0001F9F1 Chunk Embedding Audit")
        self.stdout.write(f"Chunks: {total}")
        self.stdout.write(f"\u2705 Embedded: {total - missing}")
        if missing:
            self.stdout.write(f"\u274C Missing Embedding: {missing}")
        if invalid:
            self.stdout.write(f"\u26A0\uFE0F Invalid vectors: {invalid}")
        if glossary_zero:
            self.stdout.write(f"\u26A0\uFE0F Glossary-linked but glossary_score = 0: {glossary_zero}")
