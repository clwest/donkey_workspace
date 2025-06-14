# ✅ Ω.10.w.c — Reinforcement Seeder for Mutation Testing
# 
# Purpose: Seed reinforcement logs for symbolic anchors so the mutation_score system can be validated

from django.core.management.base import BaseCommand
from django.utils import timezone
import random

from memory.models import SymbolicMemoryAnchor, AnchorReinforcementLog
from assistants.models import Assistant

TRIGGER_SOURCES = ["suggestion", "fallback", "manual"]
OUTCOMES = ["match", "miss", "fallback", "boosted"]

class Command(BaseCommand):
    help = "Seed reinforcement logs for mutation_score testing"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", required=True, help="Assistant slug")
        parser.add_argument("--count", type=int, default=20, help="How many anchors to seed")

    def handle(self, *args, **options):
        slug = options["assistant"]
        count = options["count"]

        assistant = Assistant.objects.filter(slug=slug).first()
        if not assistant:
            self.stderr.write(self.style.ERROR(f"Assistant '{slug}' not found"))
            return

        anchors = SymbolicMemoryAnchor.objects.filter(assistant=assistant).order_by("?")[:count]
        seeded = 0

        for anchor in anchors:
            for _ in range(random.randint(3, 6)):
                AnchorReinforcementLog.objects.create(
                    assistant=assistant,
                    anchor=anchor,
                    trigger_source=random.choice(TRIGGER_SOURCES),
                    outcome=random.choice(OUTCOMES),
                    score_delta=round(random.uniform(-0.5, 1.0), 2),
                    created_at=timezone.now()
                )
                seeded += 1

        self.stdout.write(self.style.SUCCESS(
            f"✅ Seeded {seeded} reinforcement logs for {anchors.count()} anchors under '{slug}'"
        ))