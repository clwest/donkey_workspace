# mcp_core/management/commands/backfill_source_files.py

from django.core.management.base import BaseCommand
from mcp_core.models import DevDoc


class Command(BaseCommand):
    help = "Backfill empty DevDoc.source_file fields using slug-based filenames"

    def handle(self, *args, **options):
        updated_count = 0

        for doc in DevDoc.objects.filter(source_file=""):
            doc.source_file = f"{doc.slug}.md"
            doc.save()
            self.stdout.write(f"💾 Set source_file for '{doc.title}' → {doc.source_file}")
            updated_count += 1

        self.stdout.write(self.style.SUCCESS(f"✅ Updated {updated_count} DevDocs."))