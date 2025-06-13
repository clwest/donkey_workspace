from django.core.management.base import BaseCommand
from django.utils import timezone
from intel_core.models import Document, DocumentChunk
from prompts.utils.token_helpers import count_tokens

class Command(BaseCommand):
    """Inspect Document chunk integrity and embedding flags."""

    help = "Inspect Document chunks and embedding metadata"

    def add_arguments(self, parser):
        parser.add_argument("--verbose", action="store_true")
        parser.add_argument("--repair", action="store_true")

    def handle(self, *args, **options):
        verbose = options.get("verbose")
        repair = options.get("repair")
        mismatched = []
        for doc in Document.objects.all().order_by("created_at"):
            chunks = DocumentChunk.objects.filter(document=doc)
            embedded = chunks.filter(embedding_status="embedded").count()
            chunk_count = chunks.count()
            meta = doc.metadata or {}
            is_embedded = meta.get("is_embedded")
            version = meta.get("embedding_version")
            meta_count = meta.get("chunk_count")
            tokens = meta.get("token_count") or doc.token_count_int
            if verbose:
                self.stdout.write(
                    f"{doc.slug} | {doc.title} | {doc.source_type} | {doc.id}"
                )
                self.stdout.write(
                    f"  chunks={chunk_count} embedded={embedded} meta_flags is_embedded={is_embedded} version={version} chunk_count={meta_count} tokens={tokens}"
                )
            if repair:
                recalculated_tokens = tokens or count_tokens(doc.content or "")
                recalculated_is_embedded = chunk_count > 0 and embedded == chunk_count
                if (
                    is_embedded != recalculated_is_embedded
                    or meta_count != chunk_count
                    or tokens != recalculated_tokens
                ):
                    mismatched.append(str(doc.id))
                    meta.update(
                        {
                            "is_embedded": recalculated_is_embedded,
                            "chunk_count": chunk_count,
                            "token_count": recalculated_tokens,
                            "embedding_version": version or "v1",
                        }
                    )
                    doc.metadata = meta
                    doc.token_count_int = recalculated_tokens
                    doc.save(update_fields=["metadata", "token_count_int"])
        if repair and mismatched:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Repaired {len(mismatched)} documents: {', '.join(mismatched)}"
                )
            )
        self.stdout.write(self.style.SUCCESS("Inspection complete"))
