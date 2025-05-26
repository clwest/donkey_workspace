from django.core.management.base import BaseCommand
from agents.models import CodexClause


class Command(BaseCommand):
    help = "Seed CodexClause records for stabilization testing"

    EXAMPLE_CLAUSES = [
        "Assistants must reflect after major symbolic changes.",
        "Clause drift is resolved by symbolic consensus.",
        "Memory value is recalculated after codex updates.",
        "Codex forks must log their divergence source.",
        "Symbolic gain should be maximized over token cost.",
    ]

    def handle(self, *args, **options):
        created = 0
        for text in self.EXAMPLE_CLAUSES:
            clause, was_created = CodexClause.objects.get_or_create(text=text)
            if was_created:
                created += 1
                self.stdout.write(f"Added clause {clause.id}")
        self.stdout.write(self.style.SUCCESS(f"Seeded {created} codex clauses."))

