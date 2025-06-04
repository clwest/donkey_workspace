from django.core.management.base import BaseCommand
from assistants.models import Assistant
from memory.models import MemoryEntry


class Command(BaseCommand):
    help = "Backfill summary field on delegation summary memories"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", help="Assistant slug", default=None)

    def handle(self, *args, **options):
        slug = options.get("assistant")
        qs = MemoryEntry.objects.filter(type="delegation_summary")
        if slug:
            qs = qs.filter(assistant__slug=slug)
        repaired = 0
        for mem in qs.filter(summary__isnull=True):
            text = mem.full_transcript or mem.event
            mem.summary = (text or "").splitlines()[0][:200]
            mem.save(update_fields=["summary"])
            repaired += 1
        self.stdout.write(
            self.style.SUCCESS(f"Repaired {repaired} delegation summaries")
        )
