from django.core.management.base import BaseCommand
from intel_core.models import DocumentChunk
from embeddings.tasks import embed_and_store


class Command(BaseCommand):
    """Embed DocumentChunks lacking embeddings."""

    help = (
        "Embed DocumentChunks that do not have embeddings. "
        "Use --only-glossary to restrict to glossary chunks."
    )

    def add_arguments(self, parser):
        parser.add_argument("--only-glossary", action="store_true")

    def handle(self, *args, **options):
        qs = DocumentChunk.objects.filter(embedding__isnull=True)
        if options.get("only_glossary"):
            qs = qs.filter(is_glossary=True)

        self.stdout.write(f"🔍 Found {qs.count()} chunks missing embeddings.")
        for chunk in qs:
            preview = chunk.text[:60].replace("\n", " ")
            self.stdout.write(f"📌 Embedding chunk {chunk.id} ({preview})")
            embed_and_store.delay(str(chunk.id))

