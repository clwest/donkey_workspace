from django.core.management.base import BaseCommand
from intel_core.models import Document
from intel_core.utils import update_document_status


class Command(BaseCommand):
    help = "Verify and correct document status"

    def add_arguments(self, parser):
        parser.add_argument("--all", action="store_true")
        parser.add_argument("--doc-id", dest="doc_id")

    def handle(self, *args, **options):
        if options.get("all"):
            docs = Document.objects.all()
        elif options.get("doc_id"):
            docs = Document.objects.filter(id=options["doc_id"])
        else:
            self.stderr.write("Provide --all or --doc-id")
            return
        for doc in docs:
            old = doc.status
            update_document_status(doc)
            if doc.status != old:
                self.stdout.write(f"{doc.title}: {old} -> {doc.status}")
        self.stdout.write(self.style.SUCCESS("Verification complete"))
