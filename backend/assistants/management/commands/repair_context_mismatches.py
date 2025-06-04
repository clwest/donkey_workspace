from django.core.management.base import BaseCommand
from assistants.models import Assistant
from memory.models import MemoryEntry
from mcp_core.models import MemoryContext


class Command(BaseCommand):
    help = "Repair context mismatches for assistant memory entries"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", type=str)

    def handle(self, *args, **options):
        slug = options["assistant"]
        assistant = Assistant.objects.get(slug=slug)
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
            f"\U0001f527 Linked {count} memory entries to context {context.id} ({assistant.slug})"
        )
