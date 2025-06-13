import logging
from django.core.management.base import BaseCommand
from memory.models import MemoryEntry
from assistants.utils.delegation_summary_engine import DelegationSummaryEngine
from assistants.utils.resolve import resolve_assistant

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Backfill summary field on delegation summary memories"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", help="Assistant slug", default=None)

    def handle(self, *args, **options):
        identifier = options.get("assistant")
        qs = MemoryEntry.objects.filter(type="delegation_summary")
        if identifier:
            assistant = resolve_assistant(identifier)
            if not assistant:
                self.stderr.write(self.style.ERROR(f"Assistant '{identifier}' not found"))
                return
            qs = qs.filter(assistant=assistant)
        repaired = 0
        for mem in qs:
            updated_fields = []
            if mem.summary is None:
                text = mem.full_transcript or mem.event
                mem.summary = (text or "").splitlines()[0][:200]
                updated_fields.append("summary")

            if mem.full_transcript is None:
                full_text = mem.summary or mem.event or ""
                if len(full_text) > 4000:
                    # use same compression logic as DelegationSummaryEngine
                    engine = DelegationSummaryEngine(mem.assistant)
                    full_text = engine._compress_history(full_text)
                mem.full_transcript = full_text
                updated_fields.append("full_transcript")
                logger.info("Updated full_transcript for %s", mem.id)

            if updated_fields:
                mem.save(update_fields=updated_fields)
                repaired += 1
        self.stdout.write(
            self.style.SUCCESS(f"Repaired {repaired} delegation summaries")
        )
