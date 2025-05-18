import os
import sys
import django
from django.utils.text import slugify

# Setup Django
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
django.setup()

from mcp_core.models import DevDoc
from intel_core.models import Document

def run():
    count = 0
    for devdoc in DevDoc.objects.all():
        if not devdoc.content:
            continue

        slug = slugify(devdoc.source_file.replace(".md", "")) if devdoc.source_file else None
        if not slug:
            continue

        # Already exists?
        if Document.objects.filter(slug=slug).exists():
            continue

        doc = Document.objects.create(
            title=devdoc.title,
            slug=slug,
            content=devdoc.content,
            source="devdoc",
            source_type="markdown",
            metadata={"devdoc_id": str(devdoc.id)},
        )
        print(f"📄 Created Document from DevDoc: {devdoc.title} → {slug}")
        count += 1

    print(f"\n✅ Created {count} new Document records from DevDocs.")

if __name__ == "__main__":
    run()