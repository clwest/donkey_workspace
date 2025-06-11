from django.core.management.base import BaseCommand
from intel_core.models import (
    Document,
    DocumentChunk,
    DocumentProgress,
    EmbeddingMetadata,
)


class Command(BaseCommand):
    help = "Validate and repair embedding linkage and progress counts for a document"

    def add_arguments(self, parser):
        parser.add_argument("--doc-id", required=True)
        parser.add_argument("--repair", action="store_true")

    def handle(self, *args, **options):
        doc_id = options["doc_id"]
        repair = options.get("repair")
        try:
            doc = Document.objects.get(id=doc_id)
        except Document.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"Document {doc_id} not found"))
            return

        chunks = DocumentChunk.objects.filter(document=doc).select_related("embedding")
        total = chunks.count()
        linked = chunks.filter(embedding__isnull=False).count()
        self.stdout.write(f"Chunks: {total} | Linked embeddings: {linked}")

        missing_link = chunks.filter(embedding__isnull=True)
        self.stdout.write(f"Missing links: {missing_link.count()}")
        if repair and missing_link.exists():
            fixed = 0
            for ch in missing_link:
                meta = EmbeddingMetadata.objects.filter(chunk__id=ch.id).first()
                if meta:
                    ch.embedding = meta
                    ch.embedding_status = "embedded"
                    ch.save(update_fields=["embedding", "embedding_status"])
                    fixed += 1
            self.stdout.write(f"Fixed {fixed} missing links")

        progress = doc.get_progress()
        if progress:
            self.stdout.write(
                f"Progress: {progress.embedded_chunks}/{progress.total_chunks} status={progress.status}"
            )
            if repair:
                doc.sync_progress()
                progress.refresh_from_db()
                self.stdout.write(
                    f"Repaired → {progress.embedded_chunks}/{progress.total_chunks} status={progress.status}"
                )
        else:
            self.stdout.write("No DocumentProgress record found")
            if repair:
                doc.sync_progress()
                prog = doc.get_progress()
                if prog:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Created progress {prog.embedded_chunks}/{prog.total_chunks}"
                        )
                    )

        self.stdout.write(self.style.SUCCESS("Validation complete"))
