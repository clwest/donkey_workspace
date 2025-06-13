from django.core.management.base import BaseCommand
from assistants.models import Assistant
from assistants.utils.resolve import resolve_assistant
from memory.models import MemoryEntry
from django.db.models import F, CharField
from django.db.models.functions import Cast


class Command(BaseCommand):
    """Inspect memory linkage health for an assistant."""

    help = "Audit MemoryEntry context links and transcripts"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", help="Assistant slug to inspect")

    def handle(self, *args, **options):
        slug = options.get("assistant")
        if slug:
            assistant = resolve_assistant(slug)
            if not assistant:
                self.stderr.write(self.style.ERROR(f"Assistant '{slug}' not found"))
                return
            qs = [assistant]
        else:
            qs = Assistant.objects.all()
        for a in qs:
            mems = MemoryEntry.objects.filter(assistant=a)
            total = mems.count()
            linked = mems.filter(context__isnull=False).count()
            orphaned = total - linked
            missing = mems.filter(full_transcript__isnull=True).count()
            # context.target_object_id is a CharField but MemoryEntry.id is a UUID
            # Cast the UUID to text for an accurate comparison
            matches = mems.filter(
                context__target_object_id=Cast(F("id"), CharField())
            ).count()
            mismatches = linked - matches
            self.stdout.write(self.style.MIGRATE_HEADING(f"Assistant: {a.slug}"))
            self.stdout.write(
                f"\U0001f9e0 Memory Entries: {total} total | {linked} linked | {orphaned} orphaned"
            )
            if missing:
                self.stdout.write(
                    f"\u26a0\ufe0f {missing} entries missing full_transcript"
                )
            self.stdout.write(f"\u2705 Context ID matches: {matches}")
            if mismatches:
                self.stdout.write(f"\u274c Context mismatches: {mismatches}")
            missing_summary = mems.filter(
                type="delegation_summary", summary__isnull=True
            ).count()
            if missing_summary:
                self.stdout.write(
                    f"\u26a0\ufe0f {missing_summary} delegation summaries missing summary"
                )
