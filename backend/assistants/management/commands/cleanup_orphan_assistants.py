from django.core.management.base import BaseCommand
from assistants.models import Assistant
from django.db import models
from assistants.utils.resolve import resolve_assistant
from memory.models import MemoryEntry

class Command(BaseCommand):
    """Identify assistants with no documents and offer cleanup."""

    help = "List or delete orphaned assistants"

    def add_arguments(self, parser):
        parser.add_argument("--delete", action="store_true", help="Delete all orphans")
        parser.add_argument("--merge-into", help="Assistant slug or id to merge orphans")

    def handle(self, *args, **options):
        orphans = Assistant.objects.annotate(doc_count=models.Count("documents")).filter(doc_count=0)
        if not orphans.exists():
            self.stdout.write("No orphan assistants found")
            return
        self.stdout.write("Orphan assistants:")
        for a in orphans:
            self.stdout.write(f"- {a.slug} ({a.id})")
        target_id = options.get("merge_into")
        if target_id:
            target = resolve_assistant(target_id)
            if not target:
                self.stderr.write(self.style.ERROR(f"Target assistant '{target_id}' not found"))
                return
            for a in orphans:
                MemoryEntry.objects.filter(assistant=a).update(assistant=target)
                a.delete()
            self.stdout.write(self.style.SUCCESS(f"Merged {len(orphans)} assistants into {target.slug}"))
        elif options.get("delete"):
            count = orphans.count()
            orphans.delete()
            self.stdout.write(self.style.SUCCESS(f"Deleted {count} assistants"))
