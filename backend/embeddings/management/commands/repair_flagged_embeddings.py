from django.core.management.base import BaseCommand
from django.utils import timezone
from embeddings.models import EmbeddingDebugTag
from embeddings.utils.link_repair import repair_embedding_link, embedding_link_matches


class Command(BaseCommand):
    help = "Repair embeddings flagged by EmbeddingDebugTag"

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        dry_run = options.get("dry_run")
        pending = EmbeddingDebugTag.objects.filter(repair_status="pending").select_related(
            "embedding"
        )
        fixed = 0
        failed = 0
        for tag in pending:
            changed = repair_embedding_link(tag.embedding, dry_run=dry_run)
            tag.repair_attempts += 1
            tag.last_attempt_at = timezone.now()
            if dry_run:
                continue
            if embedding_link_matches(tag.embedding):
                tag.repair_status = "repaired"
                tag.repaired_at = timezone.now()
                fixed += 1
            else:
                tag.repair_status = "failed" if changed else "skipped"
                failed += 1
            tag.save(update_fields=[
                "repair_status",
                "repair_attempts",
                "last_attempt_at",
                "repaired_at",
            ])
        self.stdout.write(
            f"Processed {pending.count()} tags -> repaired {fixed} failed {failed}"
        )
