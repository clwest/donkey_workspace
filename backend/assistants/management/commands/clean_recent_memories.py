from django.core.management.base import BaseCommand
from django.core.management import call_command
from assistants.utils.resolve import resolve_assistant
from memory.models import MemoryEntry
from prompts.utils.token_helpers import count_tokens


class Command(BaseCommand):
    help = "Delete meaningless recent memories for an assistant"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", required=True)

    def handle(self, *args, **options):
        identifier = options["assistant"]
        assistant = resolve_assistant(identifier)
        if not assistant:
            message = self.style.ERROR(
                f"Assistant '{identifier}' not found"
            )
            self.stderr.write(message)
            return

        qs = MemoryEntry.objects.filter(
            assistant=assistant,
            related_project__isnull=True,
            narrative_thread__isnull=True,
            thread__isnull=True,
        )

        meaningless_ids = list(
            qs.filter(
                event__icontains="couldn’t find that information"
            ).values_list("id", flat=True)
        )

        for mem in qs.exclude(id__in=meaningless_ids):
            tokens = count_tokens(mem.summary or mem.event or "")
            if tokens < 5 and mem.importance <= 2:
                meaningless_ids.append(mem.id)

        count = len(meaningless_ids)
        if count:
            MemoryEntry.objects.filter(id__in=meaningless_ids).delete()

        self.stdout.write(
            f"Removed {count} weak memories for {assistant.slug}"
        )
        # After pruning memory entries, ensure they link to the correct context
        call_command("repair_context_mismatches", assistant=assistant.slug)
