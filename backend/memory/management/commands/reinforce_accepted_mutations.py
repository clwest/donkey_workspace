from django.core.management.base import BaseCommand
from memory.models import SymbolicMemoryAnchor, AnchorReinforcementLog
from memory.services.reinforcement import reinforce_glossary_anchor

class Command(BaseCommand):
    """Backfill reinforcement memories for applied glossary mutations."""

    help = "Create reinforcement logs for applied glossary mutations"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", required=False)

    def handle(self, *args, **options):
        slug = options.get("assistant")
        anchors = SymbolicMemoryAnchor.objects.filter(mutation_status="applied")
        if slug:
            from assistants.utils.resolve import resolve_assistant
            assistant = resolve_assistant(slug)
            if not assistant:
                self.stderr.write(self.style.ERROR(f"Assistant '{slug}' not found"))
                return
            anchors = anchors.filter(assistant=assistant)
        count = 0
        for anchor in anchors:
            if not AnchorReinforcementLog.objects.filter(anchor=anchor, reason="mutation_applied").exists():
                reinforce_glossary_anchor(anchor, assistant=anchor.assistant, source="mutation_applied", score=1.0)
                count += 1
        self.stdout.write(self.style.SUCCESS(f"Reinforced {count} anchors"))
