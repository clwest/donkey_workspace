from django.core.management.base import BaseCommand
from intel_core.models import Document, DocumentProgress


class Command(BaseCommand):
    help = "Fix stale total_chunks on DocumentProgress objects"

    def handle(self, *args, **kwargs):
        fixed = 0
        for doc in Document.objects.all():
            progress = DocumentProgress.objects.filter(document=doc).first()
            if not progress:
                continue
            true_count = doc.chunks.count()
            if progress.total_chunks != true_count:
                progress.total_chunks = true_count
                progress.save(update_fields=["total_chunks"])
                fixed += 1
        self.stdout.write(
            self.style.SUCCESS(f"✅ Synced total_chunks on {fixed} documents.")
        )
