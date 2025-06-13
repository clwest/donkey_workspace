from django.core.management.base import BaseCommand
from assistants.utils.assistant_lookup import resolve_assistant
from embeddings.utils.link_repair import repair_context_embeddings
from embeddings.models import EmbeddingDriftLog
from django.utils import timezone


class Command(BaseCommand):
    help = "Repair embeddings for an assistant's memory context"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", required=True, help="Assistant slug or id")

    def handle(self, *args, **options):
        identifier = options["assistant"]
        assistant = resolve_assistant(identifier)
        if not assistant:
            self.stderr.write(self.style.ERROR(f"Assistant '{identifier}' not found"))
            return
        if not assistant.memory_context_id:
            self.stderr.write(self.style.ERROR("Assistant has no memory context"))
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
