# At the top
from django.conf import settings
import os
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from mcp_core.models import DevDoc


class Command(BaseCommand):
    help = "Seed DevDocs from the local /docs folder"

    def handle(self, *args, **options):
        DOCS_DIR = os.path.join(settings.BASE_DIR, "docs")  # ✅ Use BASE_DIR

        if not os.path.exists(DOCS_DIR):
            self.stdout.write(
                self.style.ERROR(f"❌ docs folder not found at {DOCS_DIR}")
            )
            return

        count = 0
        for filename in os.listdir(DOCS_DIR):
            if not filename.endswith(".md"):
                continue

            filepath = os.path.join(DOCS_DIR, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            title = filename.replace(".md", "").replace("-", " ").title()
            slug = slugify(title)

            doc, created = DevDoc.objects.update_or_create(
                slug=slug, defaults={"title": title, "content": content}
            )

            status = "✅ Created" if created else "♻️ Updated"
            self.stdout.write(f"{status}: {filename}")
            count += 1

        self.stdout.write(
            self.style.SUCCESS(f"🎉 Seed complete — {count} markdown files processed.")
        )
