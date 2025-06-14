from django.core.management.base import BaseCommand
from django.db import models
from assistants.models import Assistant
from memory.models import MemoryEntry
from mcp_core.models import NarrativeThread
from assistants.utils.resolve import resolve_assistant


class Command(BaseCommand):
    """Repair assistant links on MemoryEntry objects."""

    help = "Repair assistant_id for MemoryEntry records"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", help="Assistant slug to repair")
        parser.add_argument("--dry-run", action="store_true", help="Preview changes only")

    def handle(self, *args, **options):
        slug = options.get("assistant")
        dry_run = options.get("dry_run", False)
        assistants = []
        if slug:
            a = resolve_assistant(slug)
            if not a:
                self.stderr.write(self.style.ERROR(f"Assistant '{slug}' not found"))
                return
            assistants = [a]
        else:
            assistants = list(Assistant.objects.all())

        total_fixed = 0
        total_skipped = 0

        for assistant in assistants:
            self.stdout.write(self.style.MIGRATE_HEADING(f"Assistant: {assistant.slug}"))
            qs = MemoryEntry.objects.filter(assistant__isnull=True).filter(
                models.Q(context_id=assistant.memory_context_id)
                | models.Q(document__memory_context_id=assistant.memory_context_id)
            )
            scanned = qs.count()
            fixed = 0
            skipped = 0
            for mem in qs:
                if not dry_run:
                    mem.assistant = assistant
                    mem.save(update_fields=["assistant"])
                fixed += 1
            skipped = scanned - fixed
            total_fixed += fixed
            total_skipped += skipped
            self.stdout.write(f"  memories scanned={scanned} fixed={fixed} skipped={skipped}")

        # Auto-link narrative thread origin memories if missing
        threads = NarrativeThread.objects.filter(origin_memory__isnull=True, related_memories__isnull=False)
        thread_fixed = 0
        for t in threads.distinct():
            mem = t.related_memories.order_by("created_at").first()
            if mem:
                if not dry_run:
                    t.origin_memory = mem
                    t.save(update_fields=["origin_memory"])
                thread_fixed += 1
        if thread_fixed:
            self.stdout.write(f"  linked {thread_fixed} narrative threads to origin memories")

        self.stdout.write(self.style.SUCCESS(f"Total fixed: {total_fixed} | skipped: {total_skipped}"))
