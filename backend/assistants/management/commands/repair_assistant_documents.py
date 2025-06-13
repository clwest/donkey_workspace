from django.core.management.base import BaseCommand
from assistants.models import Assistant
from mcp_core.models import DevDoc
from django.db import transaction

class Command(BaseCommand):
    help = "Audit assistant document links and repair missing associations"

    def add_arguments(self, parser):
        parser.add_argument("--fix", action="store_true", help="Apply repairs")

    @transaction.atomic
    def handle(self, *args, **options):
        fix = options.get("fix")
        for a in Assistant.objects.all():
            docs = set(a.documents.all())
            assigned = set(a.assigned_documents.all())
            devdocs = DevDoc.objects.filter(linked_assistants=a)
            missing = []
            for devdoc in devdocs:
                if devdoc.linked_document and devdoc.linked_document not in docs:
                    missing.append(devdoc.linked_document)
                    self.stdout.write(
                        f"{a.slug}: missing document {devdoc.linked_document.slug} from documents"
                    )
                    if fix:
                        a.documents.add(devdoc.linked_document)
            for doc in assigned:
                if doc not in docs:
                    self.stdout.write(
                        f"{a.slug}: assigned doc {doc.slug} not in documents"
                    )
                    if fix:
                        a.documents.add(doc)
            for doc in docs:
                if a not in doc.linked_assistants.all():
                    self.stdout.write(
                        f"{a.slug}: document {doc.slug} missing reverse link"
                    )
                    if fix:
                        doc.linked_assistants.add(a)
            if not missing and not assigned - docs:
                self.stdout.write(self.style.SUCCESS(f"{a.slug}: OK"))
        if fix:
            self.stdout.write(self.style.SUCCESS("Repair complete"))
