from django.core.management.base import BaseCommand, CommandError
from assistants.models import Assistant
from assistants.utils.assistant_lookup import resolve_assistant
from memory.models import MemoryEntry
from assistants.models.thoughts import AssistantThoughtLog
from assistants.models.reflection import AssistantReflectionLog
from assistants.models.assistant import ChatSession

class Command(BaseCommand):
    help = "Promote an assistant to be the primary orchestrator"

    def add_arguments(self, parser):
        parser.add_argument("--slug", required=True)
        parser.add_argument(
            "--replace-from",
            help="Slug or ID of duplicate assistant to merge from",
        )

    def handle(self, *args, **options):
        slug = options["slug"]
        try:
            assistant = Assistant.objects.get(slug=slug)
        except Assistant.DoesNotExist:
            raise CommandError("Assistant not found")

        replace_from = options.get("replace_from")
        if replace_from:
            dup = resolve_assistant(replace_from)
            if dup and dup != assistant:
                MemoryEntry.objects.filter(assistant=dup).update(assistant=assistant)
                AssistantThoughtLog.objects.filter(assistant=dup).update(assistant=assistant)
                AssistantReflectionLog.objects.filter(assistant=dup).update(assistant=assistant)
                ChatSession.objects.filter(assistant=dup).update(assistant=assistant)
                dup.delete()
                self.stdout.write(self.style.WARNING(f"Merged data from {dup.slug} into {assistant.slug}"))

        Assistant.objects.filter(is_primary=True).update(is_primary=False)
        assistant.is_primary = True
        assistant.save()
        self.stdout.write(self.style.SUCCESS(f"{assistant.name} promoted to primary"))
