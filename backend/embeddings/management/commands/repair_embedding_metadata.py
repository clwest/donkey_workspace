from django.core.management.base import BaseCommand
from django.db.models import Q

from embeddings.models import Embedding
from embeddings.utils.repair_helpers import infer_embedding_metadata


class Command(BaseCommand):
    """Repair missing session_id or source_type on embeddings."""

    help = "Repair embedding metadata (session_id, source_type)"

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=None)
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        limit = options.get("limit")
        dry_run = options.get("dry_run")
        qs = Embedding.objects.filter(
            Q(session_id__isnull=True) | Q(source_type__isnull=True)
        )
        if limit:
            qs = qs.order_by("id")[:limit]

        repaired = 0
        scanned = 0
        for emb in qs.select_related("content_type"):
            scanned += 1
            info = infer_embedding_metadata(emb)
            if not info:
                continue
            for field, value in info.items():
                setattr(emb, field, value)
            if not dry_run:
                emb.save(update_fields=list(info.keys()))
            repaired += 1
            self.stdout.write(f"Repaired {emb.id} -> {info}")
        self.stdout.write(f"Scanned {scanned} | repaired {repaired}")
