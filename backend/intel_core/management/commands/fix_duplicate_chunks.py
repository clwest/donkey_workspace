from django.core.management.base import BaseCommand
from intel_core.models import Document
from intel_core.utils import dedupe_document_chunks


class Command(BaseCommand):
    help = "Remove duplicate chunks for a document"

    def add_arguments(self, parser):
        parser.add_argument("--doc-id", required=True, dest="doc_id")

    def handle(self, *args, **options):
        doc_id = options["doc_id"]
        document = Document.objects.filter(id=doc_id).first()
        if not document:
            self.stderr.write(self.style.ERROR("Document not found"))
            return
        removed = dedupe_document_chunks(document)
        self.stdout.write(self.style.SUCCESS(f"Removed {removed} duplicates"))
