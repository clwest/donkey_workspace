from django.core.management.base import BaseCommand
from assistants.models import Assistant
from embeddings.utils.link_repair import repair_context_embeddings
from embeddings.models import EmbeddingDriftLog
from django.utils import timezone


class Command(BaseCommand):
    help = "Repair embeddings for an assistant's memory context"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", required=True, help="Assistant slug or id")

    def handle(self, *args, **options):
        identifier = options["assistant"]
        assistant = (
            Assistant.objects.filter(id=identifier).first()
            or Assistant.objects.filter(slug=identifier).first()
        )
        if not assistant or not assistant.memory_context_id:
            self.stderr.write(self.style.ERROR("Assistant or context not found"))
            return
        result = repair_context_embeddings(assistant.memory_context_id, verbose=True)
        EmbeddingDriftLog.objects.create(
            assistant=assistant,
            context_id=assistant.memory_context_id,
            model_name="repair_cli",
            mismatched_count=result["scanned"],
            orphaned_count=0,
            repaired_count=result["fixed"],
            repair_attempted_at=timezone.now(),
            repair_success_count=result["fixed"],
            repair_failure_count=result["skipped"],
        )
        self.stdout.write(
            self.style.SUCCESS(
                f"Repaired {result['fixed']} of {result['scanned']} embeddings"
            )
        )
