from django.core.management.base import BaseCommand
from django.utils import timezone
from embeddings.models import EmbeddingDebugTag
from embeddings.utils.link_repair import repair_embedding_link


class Command(BaseCommand):
    help = "Repair embeddings flagged by EmbeddingDebugTag"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        dry_run = options.get("dry_run")
        pending = EmbeddingDebugTag.objects.filter(status="pending").select_related(
            "embedding"
        )
        fixed = 0
        skipped = 0
        for tag in pending:
            changed = repair_embedding_link(tag.embedding, dry_run=dry_run)
            if changed:
                tag.status = "repaired"
                tag.repaired_at = timezone.now()
                tag.save(update_fields=["status", "repaired_at"])
                fixed += 1
            else:
                if not dry_run:
                    tag.status = "ignored"
                    tag.save(update_fields=["status"])
                skipped += 1
        self.stdout.write(
            f"Processed {pending.count()} tags -> fixed {fixed} skipped {skipped}"
        )
