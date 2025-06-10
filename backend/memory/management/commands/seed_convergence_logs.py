from django.core.management.base import BaseCommand
from assistants.models import Assistant
from memory.models import SymbolicMemoryAnchor, AnchorConvergenceLog
from django.utils import timezone
import logging

class Command(BaseCommand):
    help = "Seed mock AnchorConvergenceLog entries"
    logger = logging.getLogger(__name__)

    def handle(self, *args, **options):
        assistants = Assistant.objects.all()
        anchors = SymbolicMemoryAnchor.objects.all()
        self.stdout.write(f"Assistants available: {assistants.count()}")
        self.stdout.write(f"Anchors available: {anchors.count()}")

        assistant = assistants.first()
        anchor = anchors.first()

        if not assistants.exists():
            self.stdout.write(self.style.WARNING("No assistants found"))
            return

        if not anchors.exists():
            self.stdout.write(self.style.WARNING("No anchors found, seeding dummy"))
            anchor = SymbolicMemoryAnchor.objects.create(
                slug="dummy-anchor",
                label="Dummy Anchor",
                description="Auto-created by seed_convergence_logs",
            )
            self.stdout.write(f"Created dummy anchor {anchor.slug}")

        AnchorConvergenceLog.objects.all().delete()
        for i in range(3):
            self.logger.debug("Creating convergence log %s", i)
            AnchorConvergenceLog.objects.create(
                anchor=anchor,
                assistant=assistant,
                guidance_used=i % 2 == 0,
                retried=i % 2 == 1,
                final_score=0.5 + i * 0.2,
                created_at=timezone.now() - timezone.timedelta(days=3 - i),
            )
        self.stdout.write(self.style.SUCCESS("Seeded convergence logs."))
