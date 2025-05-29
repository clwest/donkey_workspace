from django.core.management.base import BaseCommand
from assistants.models import Assistant
from memory.models import SymbolicMemoryAnchor, AnchorConvergenceLog
from django.utils import timezone

class Command(BaseCommand):
    help = "Seed mock AnchorConvergenceLog entries"

    def handle(self, *args, **options):
        assistant = Assistant.objects.first()
        anchor = SymbolicMemoryAnchor.objects.first()
        if not assistant or not anchor:
            self.stdout.write(self.style.WARNING("No assistant or anchor found"))
            return

        AnchorConvergenceLog.objects.all().delete()
        for i in range(3):
            AnchorConvergenceLog.objects.create(
                anchor=anchor,
                assistant=assistant,
                guidance_used=i % 2 == 0,
                retried=i % 2 == 1,
                final_score=0.5 + i * 0.2,
                created_at=timezone.now() - timezone.timedelta(days=3 - i),
            )
        self.stdout.write(self.style.SUCCESS("Seeded convergence logs."))
