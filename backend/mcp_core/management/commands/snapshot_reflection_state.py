from django.core.management.base import BaseCommand
from django.utils import timezone
import os
import json

from assistants.models.reflection import AssistantReflectionLog
from memory.models import ReflectionReplayLog, SymbolicMemoryAnchor
from assistants.serializers import AssistantReflectionLogSerializer
from assistants.serializers import ReflectionReplayLogSerializer

EXPORT_DIR = "exports"

class Command(BaseCommand):
    help = "Snapshot assistant reflection and replay logs with anchor boosts"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", dest="assistant", default=None)

    def handle(self, *args, **options):
        os.makedirs(EXPORT_DIR, exist_ok=True)
        assistant_slug = options.get("assistant")
        
        reflections = AssistantReflectionLog.objects.all()
        replays = ReflectionReplayLog.objects.all()
        if assistant_slug:
            from assistants.utils.resolve import resolve_assistant
            assistant = resolve_assistant(assistant_slug)
            if not assistant:
                self.stderr.write(self.style.ERROR(f"Assistant '{assistant_slug}' not found"))
                return
            reflections = reflections.filter(assistant=assistant)
            replays = replays.filter(assistant=assistant)

        reflection_data = AssistantReflectionLogSerializer(reflections, many=True).data
        replay_data = ReflectionReplayLogSerializer(replays, many=True).data
        anchor_data = list(
            SymbolicMemoryAnchor.objects.values("label", "score_weight")
        )

        data = {
            "timestamp": timezone.now().isoformat(),
            "assistant": assistant_slug,
            "reflections": reflection_data,
            "replay_logs": replay_data,
            "anchors": anchor_data,
        }

        filename = f"reflection_state_{timezone.now().strftime('%Y%m%d_%H%M%S')}.json"
        path = os.path.join(EXPORT_DIR, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        self.stdout.write(self.style.SUCCESS(f"Snapshot saved to {path}"))
