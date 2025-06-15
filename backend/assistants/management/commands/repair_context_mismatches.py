from django.core.management.base import BaseCommand
from assistants.utils.resolve import resolve_assistant
from memory.models import MemoryEntry
from mcp_core.models import MemoryContext


class Command(BaseCommand):
    help = "Repair context mismatches for assistant memory entries"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", type=str)

    def handle(self, *args, **options):
        identifier = options["assistant"]
        assistant = resolve_assistant(identifier)
        if not assistant:
            message = self.style.ERROR(
                f"Assistant '{identifier}' not found"
            )
            self.stderr.write(message)
            return
        context = assistant.memory_context

        if not context:
            context, _ = MemoryContext.objects.get_or_create(
                content=f"{assistant.slug} context"
            )
            assistant.memory_context = context
            assistant.save(update_fields=["memory_context"])

        count = MemoryEntry.objects.filter(
            assistant=assistant, context__isnull=True
        ).update(context=context)
        self.stdout.write(
            (
                f"\U0001f527 Linked {count} memory entries "
                f"to context {context.id} ({assistant.slug})"
            )
        )
