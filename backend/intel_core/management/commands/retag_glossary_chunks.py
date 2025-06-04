from django.core.management.base import BaseCommand
from assistants.models import Assistant
from intel_core.utils.glossary_tagging import retag_glossary_chunks


class Command(BaseCommand):
    """Re-scan chunks for glossary anchor matches."""

    help = "Recalculate glossary tags by matching anchor slugs in chunks"

    def add_arguments(self, parser):
        parser.add_argument("--assistant", required=True, type=str)
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--reset", action="store_true")

    def handle(self, *args, **options):
        assistant_slug = options["assistant"]
        dry_run = options.get("dry_run", False)
        reset = options.get("reset", False)

        try:
            assistant = Assistant.objects.get(slug=assistant_slug)
        except Assistant.DoesNotExist:
            self.stderr.write(
                self.style.ERROR(f"Assistant '{assistant_slug}' not found.")
            )
            return

        if reset:
            from intel_core.models import DocumentChunk

            reset_count = DocumentChunk.objects.filter(
                document__linked_assistants=assistant
            ).update(is_glossary=False)
            self.stdout.write(f"Reset is_glossary on {reset_count} chunks")

        results = retag_glossary_chunks(assistant, dry_run=dry_run)
        for slug, info in results.items():
            self.stdout.write(self.style.SUCCESS(f"✔️ {slug}: {len(info)} chunks"))
