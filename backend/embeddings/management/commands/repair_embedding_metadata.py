from django.core.management.base import BaseCommand
from django.db.models import Q

from embeddings.models import Embedding, EmbeddingRepairLog
from embeddings.utils.repair_helpers import infer_embedding_metadata


class Command(BaseCommand):
    """Repair missing session_id or source_type on embeddings."""

    help = "Repair embedding metadata (session_id, source_type)"

    def add_arguments(self, parser):
        parser.add_argument("--limit", type=int, default=None)
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument(
            "--force",
            action="store_true",
            help="Overwrite existing metadata if mismatched",
        )
        parser.add_argument(
            "--summary",
            action="store_true",
            help="Print summary of fixes",
        )

    def handle(self, *args, **options):
        limit = options.get("limit")
        dry_run = options.get("dry_run")
        force = options.get("force")
        show_summary = options.get("summary")

        if force:
            qs = Embedding.objects.all()
        else:
            qs = Embedding.objects.filter(
                Q(session_id__isnull=True) | Q(source_type__isnull=True)
            )
        if limit:
            qs = qs.order_by("id")[:limit]

        summary = {"scanned": 0, "repaired": 0, "skipped": 0}
        for emb in qs.select_related("content_type"):
            summary["scanned"] += 1
            info = infer_embedding_metadata(emb)
            if not info:
                summary["skipped"] += 1
                continue

            changed_fields = {}
            for field, value in info.items():
                current = getattr(emb, field)
                if force or current is None or current != value:
                    setattr(emb, field, value)
                    changed_fields[field] = value
            if changed_fields:
                if not dry_run:
                    emb.save(update_fields=list(changed_fields.keys()))
                    EmbeddingRepairLog.objects.create(
                        embedding=emb,
                        action="metadata_fix",
                        notes=str(changed_fields),
                    )
                summary["repaired"] += 1
                self.stdout.write(f"Repaired {emb.id} -> {changed_fields}")
            else:
                summary["skipped"] += 1

        if show_summary:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Scanned {summary['scanned']} | repaired {summary['repaired']} | skipped {summary['skipped']}"
                )
            )
        else:
            self.stdout.write(
                f"Scanned {summary['scanned']} | repaired {summary['repaired']}"
            )
