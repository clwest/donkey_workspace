from django.core.management.base import BaseCommand
from django.db.models import Q
from intel_core.models import DocumentChunk

class Command(BaseCommand):
    """Mark chunks with anchors but zero glossary score as drifting."""

    help = "Detect drifting chunks and set is_drifting flag"

    def handle(self, *args, **options):
        qs = DocumentChunk.objects.filter(
            embedding_status="embedded",
            embedding_valid=True,
            anchor__isnull=False,
        )
        total = qs.count()
        drifted = 0
        for chunk in qs:
            drifting = chunk.glossary_score == 0
            if drifting != chunk.is_drifting:
                chunk.is_drifting = drifting
                chunk.save(update_fields=["is_drifting"])
            if drifting:
                drifted += 1
        self.stdout.write(f"Checked {total} chunks. Drift detected: {drifted}")

