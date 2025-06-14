from django.core.management.base import BaseCommand
from assistants.utils.resolve import resolve_assistant
from memory.models import SymbolicMemoryAnchor, AnchorReinforcementLog
from django.db.models import Sum


class Command(BaseCommand):
    help = "Forecast mutation success based on recent reinforcement history"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", required=True)

    def handle(self, *args, **options):
        assistant = resolve_assistant(options["assistant"])
        if not assistant:
            self.stderr.write(self.style.ERROR("Assistant not found"))
            return
        anchors = SymbolicMemoryAnchor.objects.filter(assistant=assistant)
        for anchor in anchors:
            logs = anchor.reinforcement_logs.order_by("-created_at")[:5]
            streak = sum(1 for l in logs if l.score_delta > 0) - sum(
                1 for l in logs if l.score_delta < 0
            )
            delta = anchor.mutation_score_delta or 0.0
            forecast = round(delta * 0.7 + streak * 0.3, 3)
            anchor.mutation_forecast_score = forecast
            anchor.save(update_fields=["mutation_forecast_score"])
            trend = "rising" if forecast > 0 else "falling" if forecast < 0 else "stable"
            self.stdout.write(f"{anchor.slug}: {forecast:.3f} ({trend})")
