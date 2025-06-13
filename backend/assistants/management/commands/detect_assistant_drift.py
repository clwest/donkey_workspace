from django.core.management.base import BaseCommand
from assistants.models import Assistant, SpecializationDriftLog
from assistants.utils.resolve import resolve_assistant
from assistants.utils.drift_detection import analyze_specialization_drift


class Command(BaseCommand):
    help = "Analyze assistants for specialization drift and log results"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", help="Slug of assistant to analyze")

    def handle(self, *args, **options):
        identifier = options.get("assistant")
        qs = Assistant.objects.filter(is_active=True)
        if identifier:
            assistant = resolve_assistant(identifier)
            if not assistant:
                self.stderr.write(self.style.ERROR(f"Assistant '{identifier}' not found"))
                return
            qs = qs.filter(id=assistant.id)
        for assistant in qs:
            result = analyze_specialization_drift(assistant)
            if result.get("flagged"):
                SpecializationDriftLog.objects.create(
                    assistant=assistant,
                    drift_score=result["drift_score"],
                    summary=result["summary"],
                    trigger_type="manual",
                    auto_flagged=False,
                )
                self.stdout.write(
                    self.style.WARNING(
                        f"Drift detected for {assistant.name} ({result['drift_score']:.2f})"
                    )
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(
                        f"{assistant.name} OK ({result['drift_score']:.2f})"
                    )
                )
