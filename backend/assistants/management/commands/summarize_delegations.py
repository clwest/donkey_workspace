from django.core.management.base import BaseCommand
from assistants.utils.resolve import resolve_assistant
from assistants.utils.delegation_summary_engine import DelegationSummaryEngine


class Command(BaseCommand):
    help = "Generate a delegation summary for an assistant"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", help="Assistant slug")
        parser.add_argument("--all", action="store_true", help="Summarize all assistants")

    def handle(self, *args, **options):
        slug = options.get("assistant")
        all_mode = options.get("all")
        if not slug and not all_mode:
            self.stderr.write("Provide --assistant=slug or --all")
            return

        from assistants.models import Assistant
        qs = Assistant.objects.all()
        if slug:
            assistant = resolve_assistant(slug)
            if not assistant:
                self.stderr.write(self.style.ERROR(f"Assistant '{slug}' not found"))
                return
            qs = qs.filter(id=assistant.id)

        for assistant in qs:
            engine = DelegationSummaryEngine(assistant)
            entry = engine.summarize_delegations()
            preview = entry.event.splitlines()[0][:80]
            self.stdout.write(
                self.style.SUCCESS(
                    f"{assistant.slug}: saved {entry.id} at {entry.created_at:%Y-%m-%d %H:%M}"
                )
            )
            self.stdout.write(preview)
