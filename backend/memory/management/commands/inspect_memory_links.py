from django.core.management.base import BaseCommand
from assistants.models import Assistant
from memory.models import MemoryEntry
from django.db.models import F

class Command(BaseCommand):
    """Inspect memory linkage health for an assistant."""

    help = "Audit MemoryEntry context links and transcripts"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", help="Assistant slug to inspect")

    def handle(self, *args, **options):
        slug = options.get("assistant")
        qs = Assistant.objects.filter(slug=slug) if slug else Assistant.objects.all()
        for a in qs:
            mems = MemoryEntry.objects.filter(assistant=a)
            total = mems.count()
            linked = mems.filter(context__isnull=False).count()
            orphaned = total - linked
            missing = mems.filter(full_transcript__isnull=True).count()
            matches = mems.filter(context__target_object_id=F("id")).count()
            mismatches = linked - matches
            self.stdout.write(self.style.MIGRATE_HEADING(f"Assistant: {a.slug}"))
            self.stdout.write(
                f"\U0001f9e0 Memory Entries: {total} total | {linked} linked | {orphaned} orphaned"
            )
            if missing:
                self.stdout.write(f"\u26A0\uFE0F {missing} entries missing full_transcript")
            self.stdout.write(f"\u2705 Context ID matches: {matches}")
            if mismatches:
                self.stdout.write(f"\u274C Context mismatches: {mismatches}")
