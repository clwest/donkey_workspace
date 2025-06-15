from django.core.management.base import BaseCommand
from assistants.utils.resolve import resolve_assistant
from assistants.models import Assistant
from memory.models import SymbolicMemoryAnchor, RAGGroundingLog
import json


class Command(BaseCommand):
    help = "Export trust metrics for anchors grouped by assistant"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", help="Assistant slug or id", required=False)
        parser.add_argument(
            "--output", help="Optional output path for JSON", required=False
        )

    def handle(self, *args, **options):
        slug = options.get("assistant")
        out_path = options.get("output")
        if slug:
            assistant = resolve_assistant(slug)
            if not assistant:
                self.stderr.write(self.style.ERROR(f"Assistant '{slug}' not found"))
                return
            assistants = [assistant]
        else:
            assistants = Assistant.objects.all()

        data = {}
        for assistant in assistants:
            anchors = SymbolicMemoryAnchor.objects.filter(assistant=assistant).order_by(
                "slug"
            )
            rows = []
            for a in anchors:
                fb_count = (
                    RAGGroundingLog.objects.filter(
                        assistant=assistant,
                        expected_anchor=a.slug,
                        fallback_triggered=True,
                    )
                    .only("id", "created_at")
                    .count()
                )
                trend = (
                    "rising"
                    if a.mutation_forecast_score > 0
                    else "falling" if a.mutation_forecast_score < 0 else "stable"
                )
                rows.append(
                    {
                        "slug": a.slug,
                        "mutation_score": a.mutation_score,
                        "is_trusted": a.is_trusted,
                        "forecast_trend": trend,
                        "fallback_count": fb_count,
                    }
                )
                self.stdout.write(
                    f"{assistant.slug} | {a.slug} | score={a.mutation_score:.2f} | trusted={a.is_trusted} | {trend} | fb={fb_count}"
                )
            data[assistant.slug] = rows

        if out_path:
            with open(out_path, "w", encoding="utf-8") as fh:
                json.dump(data, fh, indent=2)
            self.stdout.write(self.style.SUCCESS(f"Exported to {out_path}"))
