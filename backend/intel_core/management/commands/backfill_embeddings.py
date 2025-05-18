from django.core.management.base import BaseCommand
from intel_core.models import Document
from embeddings.helpers import generate_embedding


class Command(BaseCommand):
    help = "Backfill embeddings for documents without embeddings."

    def handle(self, *args, **kwargs):
        documents = Document.objects.filter(embedding__isnull=True)
        for doc in documents:
            embedding = generate_embedding(doc.content)
            if embedding:
                doc.embedding = embedding
                doc.save()
                self.stdout.write(f"Updated embedding for: {doc.title}")
