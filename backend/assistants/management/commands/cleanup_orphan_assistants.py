from django.core.management.base import BaseCommand, CommandError
from assistants.models import Assistant
from assistants.models.thoughts import AssistantThoughtLog
from assistants.models.reflection import AssistantReflectionLog
from assistants.models.assistant import ChatSession, AssistantProject
from memory.models import MemoryEntry
from assistants.utils.assistant_lookup import resolve_assistant


class Command(BaseCommand):
    help = "Find assistants with no documents, projects, memory, or usage"

    def add_arguments(self, parser):
        parser.add_argument("--delete", action="store_true", help="Delete orphans")
        parser.add_argument("--merge-into", help="Assistant slug/UUID to merge data into")
        parser.add_argument("--dry-run", action="store_true", help="Only list orphans")

    def handle(self, *args, **options):
        target = None
        if options.get("merge_into"):
            target = resolve_assistant(options["merge_into"])
            if not target:
                raise CommandError("Merge target assistant not found")

        orphans = []
        for a in Assistant.objects.all():
            if (
                a.documents.exists()
                or a.assistantproject_set.exists()
                or MemoryEntry.objects.filter(assistant=a).exists()
                or ChatSession.objects.filter(assistant=a).exists()
                or AssistantThoughtLog.objects.filter(assistant=a).exists()
                or AssistantReflectionLog.objects.filter(assistant=a).exists()
            ):
                continue
            orphans.append(a)

        self.stdout.write(f"Found {len(orphans)} orphan assistants")
        for a in orphans:
            self.stdout.write(f"- {a.slug} ({a.id}) created {a.created_at:%Y-%m-%d}")
            if not options["dry_run"]:
                if target:
                    MemoryEntry.objects.filter(assistant=a).update(assistant=target)
                    AssistantThoughtLog.objects.filter(assistant=a).update(assistant=target)
                    AssistantReflectionLog.objects.filter(assistant=a).update(assistant=target)
                    ChatSession.objects.filter(assistant=a).update(assistant=target)
                    a.documents.clear()
                    a.assigned_documents.clear()
                    a.assistantproject_set.update(assistant=target)
                if options["delete"]:
                    a.delete()
                    self.stdout.write(self.style.SUCCESS(f"Deleted {a.slug}"))
