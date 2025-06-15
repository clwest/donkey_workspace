# ✅ Ω.10.w.d — Fix Mutation Score Calculation Logic
# 
# Purpose: Ensure that mutation scores are properly calculated from reinforcement logs

from django.core.management.base import BaseCommand
from memory.models import SymbolicMemoryAnchor, AnchorReinforcementLog
from assistants.models import Assistant
from django.db.models import Sum
from assistants.utils.thought_logger import log_symbolic_thought

class Command(BaseCommand):
    help = "Recalculate mutation_score for all symbolic anchors based on reinforcement logs"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", required=True, help="Assistant slug")
        parser.add_argument("--verbose", action="store_true", help="Print scored anchors")

    def handle(self, *args, **options):
        slug = options["assistant"]
        verbose = options["verbose"]

        assistant = Assistant.objects.filter(slug=slug).first()
        if not assistant:
            self.stderr.write(self.style.ERROR(f"Assistant '{slug}' not found"))
            return

        anchors = SymbolicMemoryAnchor.objects.filter(assistant=assistant)
        updated = 0

        for anchor in anchors:
            logs = AnchorReinforcementLog.objects.filter(anchor=anchor)
            if not logs.exists():
                anchor.mutation_score = 0.0
                anchor.save()
                continue

            score = logs.aggregate(s=Sum("score_delta"))["s"] or 0.0
            anchor.mutation_score = round(score, 3)
            anchor.save()
            updated += 1

            if verbose:
                self.stdout.write(f"{anchor.slug:<30}  {anchor.mutation_score:.3f}")

        self.stdout.write(self.style.SUCCESS(
            f"✅ Recalculated mutation_score for {updated} anchors under '{slug}'"
        ))

        log_symbolic_thought(
            assistant,
            category="repair",
            thought=f"Recalculated mutation_score for {updated} anchors",
            thought_type="update",
            tool_name="mutation_score_recalc",
            tool_result_summary=f"{updated} anchors",
            origin="diagnostic-loop",
        )
