from django.core.management.base import BaseCommand
from assistants.utils.resolve import resolve_assistant
from assistants.utils.assistant_reflection_engine import reflect_on_tool_usage
from assistants.models import Assistant

class Command(BaseCommand):
    help = "Generate tool usage reflections for an assistant or all assistants"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", help="Assistant slug or id")
        parser.add_argument("--all", action="store_true")

    def handle(self, *args, **opts):
        assistants = []
        if opts.get("all"):
            assistants = list(Assistant.objects.all())
        elif opts.get("assistant"):
            a = resolve_assistant(opts["assistant"])
            if not a:
                self.stderr.write(self.style.ERROR("Assistant not found"))
                return
            assistants = [a]
        else:
            self.stderr.write("Provide --assistant or --all")
            return

        total = 0
        for a in assistants:
            logs = reflect_on_tool_usage(a)
            total += len(logs)
            self.stdout.write(f"{a.slug}: {len(logs)} reflections")
        self.stdout.write(self.style.SUCCESS(f"Created {total} reflections"))
