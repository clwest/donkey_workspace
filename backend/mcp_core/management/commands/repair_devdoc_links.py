from django.core.management.base import BaseCommand
from mcp_core.models import DevDoc
from intel_core.models import Document


class Command(BaseCommand):
    help = "Repair DevDoc.linked_document references"

    def handle(self, *args, **options):
        updated = 0
        unmatched = []
        for devdoc in DevDoc.objects.all():
            if devdoc.linked_document_id:
                continue
            doc = Document.objects.filter(slug=devdoc.slug).first()
            if not doc:
                doc = Document.objects.filter(
                    title__iexact=devdoc.title.strip()
                ).first()
            if doc:
                devdoc.linked_document = doc
                devdoc.save(update_fields=["linked_document"])
                updated += 1
                self.stdout.write(f"✓ Linked {devdoc.slug} -> {doc.slug}")
            else:
                unmatched.append(devdoc.slug)
        if unmatched:
            self.stdout.write(
                self.style.WARNING(f"Unmatched DevDocs: {', '.join(unmatched)}")
            )
        self.stdout.write(self.style.SUCCESS(f"Repaired {updated} DevDocs"))
