from django.core.management.base import BaseCommand
from django.contrib.contenttypes.models import ContentType
import json

from embeddings.models import Embedding
from memory.models import MemoryEntry
from intel_core.models import DocumentChunk
from prompts.models import Prompt


class Command(BaseCommand):
    help = "Audit embeddings for content link consistency"

    def add_arguments(self, parser):
        parser.add_argument(
            "--export",
            help="Path to export mismatched rows as JSON",
            default=None,
        )

    def handle(self, *args, **options):
        ct_memory = ContentType.objects.get_for_model(MemoryEntry)
        ct_chunk = ContentType.objects.get_for_model(DocumentChunk)
        ct_prompt = ContentType.objects.get_for_model(Prompt)
        allowed = {ct_memory.id, ct_chunk.id, ct_prompt.id}

        mismatches = []
        total = Embedding.objects.count()
        for emb in Embedding.objects.select_related("content_type"):
            ct = emb.content_type
            obj = emb.content_object
            expected = None
            if ct and emb.object_id:
                expected = f"{ct.model}:{emb.object_id}"
            if (
                not ct
                or ct.id not in allowed
                or obj is None
                or emb.content_id != expected
            ):
                mismatches.append(
                    {
                        "id": str(emb.id),
                        "content_id": emb.content_id,
                        "expected": expected,
                        "content_type": ct.model if ct else None,
                        "object_exists": obj is not None,
                    }
                )

        self.stdout.write(f"Embeddings scanned: {total}")
        self.stdout.write(f"Mismatches found: {len(mismatches)}")

        export = options.get("export")
        if export:
            with open(export, "w", encoding="utf-8") as fh:
                json.dump(mismatches, fh, indent=2)
            self.stdout.write(f"Exported details to {export}")
        else:
            for m in mismatches[:10]:
                self.stdout.write(str(m))
