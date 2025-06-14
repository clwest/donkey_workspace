from django.core.management.base import BaseCommand
from django.utils import timezone
from assistants.utils.resolve import resolve_assistant
from assistants.models import Assistant
from assistants.models.diagnostics import AssistantDiagnosticReport
from assistants.growth_rules import GROWTH_RULES
from assistants.utils.trust_profile import compute_trust_score

class Command(BaseCommand):
    help = "Backfill growth stage and points using diagnostics and trust score"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", required=False, help="Assistant slug or id")

    def handle(self, *args, **options):
        identifier = options.get("assistant")
        if identifier:
            assistants = [resolve_assistant(identifier)] if resolve_assistant(identifier) else []
            if not assistants:
                self.stderr.write(self.style.ERROR(f"Assistant '{identifier}' not found"))
                return
        else:
            assistants = Assistant.objects.all()
        for a in assistants:
            if not a.nurture_started_at:
                a.growth_stage = 0
                a.save(update_fields=["growth_stage"])
                continue
            report = (
                AssistantDiagnosticReport.objects.filter(assistant=a).order_by("-generated_at").first()
            )
            trust = compute_trust_score(a)["score"]
            points = trust // 10
            if report:
                points += int((1 - report.fallback_rate) * 5)
                points += int(report.glossary_success_rate * 5)
            a.growth_points = points
            stage = 0
            for s, rule in sorted(GROWTH_RULES.items()):
                if points >= rule["threshold"]:
                    stage = s
            old_stage = a.growth_stage
            a.growth_stage = stage
            if stage > old_stage and not a.growth_unlocked_at:
                a.growth_unlocked_at = timezone.now()
            a.save(update_fields=["growth_points", "growth_stage", "growth_unlocked_at"])
            self.stdout.write(f"{a.slug}: stage {a.growth_stage} points {points}")

