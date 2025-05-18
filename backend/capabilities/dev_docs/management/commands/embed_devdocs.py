from django.core.management.base import BaseCommand
from mcp_core.models import DevDoc
from embeddings.helpers.helpers_processing import generate_embedding
from tqdm import tqdm

class Command(BaseCommand):
    help = "Generate and save vector embeddings for all DevDocs."

    def handle(self, *args, **options):
        docs = DevDoc.objects.all()
        embedded = 0
        skipped = 0
        failed = 0

        for doc in tqdm(docs, desc="Embedding DevDocs"):
            if doc.embedding:
                skipped += 1
                continue

            try:
                embedding = generate_embedding(doc.content)
                doc.embedding = embedding
                doc.save()
                self.stdout.write(f"✅ Embedded: {doc.title}")
                embedded += 1
            except Exception as e:
                self.stderr.write(f"❌ Failed to embed: {doc.title} | {str(e)}")
                failed += 1

        self.stdout.write("\n✅ DevDoc embedding complete.")
        self.stdout.write(f"✔️ Embedded: {embedded}")
        self.stdout.write(f"⏭️ Skipped: {skipped}")
        self.stdout.write(f"❌ Failed: {failed}")