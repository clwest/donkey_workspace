import json
from django.core.management.base import BaseCommand
from assistants.models import Assistant, AssistantReflectionLog
from embeddings.models import EmbeddingDriftLog


class Command(BaseCommand):
    help = "Export assistant document links, context IDs and reflection history"

    def add_arguments(self, parser):
        parser.add_argument("--format", choices=["json", "markdown"], default="json")
        parser.add_argument("--output", help="File path to write export")

    def handle(self, *args, **options):
        fmt = options["format"]
        output = options.get("output")
        target = open(output, "w", encoding="utf-8") if output else self.stdout

        data = []
        for a in Assistant.objects.all().order_by("slug"):
            row = {
                "id": str(a.id),
                "slug": a.slug,
                "memory_context_id": str(a.memory_context_id) if a.memory_context_id else None,
                "document_ids": list(a.documents.values_list("id", flat=True)),
                "reflection_ids": list(
                    a.assistant_reflections.order_by("-created_at").values_list("id", flat=True)
                ),
                "drift_logs": list(
                    EmbeddingDriftLog.objects.filter(assistant=a)
                    .order_by("-timestamp")[:5]
                    .values("timestamp", "context_id", "mismatched_count", "repaired_count")
                ),
            }
            data.append(row)

        if fmt == "json":
            json.dump(data, target, indent=2, default=str)
        else:
            target.write("| Assistant | Context ID | Documents | Reflections |\n")
            target.write("|-----------|------------|-----------|-------------|\n")
            for row in data:
                target.write(
                    f"| {row['slug']} | {row['memory_context_id'] or ''} | {len(row['document_ids'])} | {len(row['reflection_ids'])} |\n"
                )

        if output:
            target.close()
