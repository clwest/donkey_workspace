from django.core.management.base import BaseCommand
from assistants.models import AssistantReflectionLog
from assistants.utils.thought_logger import (
    log_symbolic_thought,
    get_or_create_symbolic_thread,
)

class Command(BaseCommand):
    help = "Backfill AssistantThoughtLog entries from reflection logs"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", help="Assistant slug", required=False)

    def handle(self, *args, **options):
        slug = options.get("assistant")
        qs = AssistantReflectionLog.objects.all().order_by("-created_at")
        if slug:
            qs = qs.filter(assistant__slug=slug)
        count = 0
        for r in qs:
            if not r.assistant:
                continue
            if r.thoughts.exists():
                continue
            thread = get_or_create_symbolic_thread(r.assistant, "reflection")
            log_symbolic_thought(
                r.assistant,
                category="reflection",
                thought=r.summary,
                thought_type="reflection",
                project=r.project,
                tool_name="reflection_engine",
                summoned_memory_ids=r.generated_from_memory_ids or [],
                narrative_thread=thread,
            )
            count += 1
        self.stdout.write(self.style.SUCCESS(f"Backfilled {count} reflection thoughts"))
