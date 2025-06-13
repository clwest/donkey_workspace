from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from assistants.models.reflection import AssistantReflectionLog
from memory.utils import replay_reflection

class Command(BaseCommand):
    help = "Replay past reflections with updated glossary anchors"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", dest="assistant", default=None)
        parser.add_argument("--since", dest="since", default="7d")
        parser.add_argument("--only-mutated", action="store_true")

    def handle(self, *args, **options):
        qs = AssistantReflectionLog.objects.all()
        if options["assistant"]:
            from assistants.utils.resolve import resolve_assistant

            assistant = resolve_assistant(options["assistant"])
            if not assistant:
                self.stderr.write(self.style.ERROR(f"Assistant '{options['assistant']}' not found"))
                return
            qs = qs.filter(assistant=assistant)
        since = options.get("since", "7d")
        if since.endswith("d"):
            try:
                days = int(since[:-1])
                qs = qs.filter(created_at__gte=timezone.now() - timedelta(days=days))
            except ValueError:
                pass
        count = 0
        for ref in qs:
            replay_reflection(ref)
            count += 1
        self.stdout.write(self.style.SUCCESS(f"Replayed {count} reflections"))
