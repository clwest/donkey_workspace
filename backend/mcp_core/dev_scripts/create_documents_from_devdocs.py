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
from mcp_core.utils.devdoc_tools import link_document_to_devdoc, create_summary_from_doc


def run():
    count = 0
    for devdoc in DevDoc.objects.all():
        if not devdoc.content:
            continue

        slug = (
            slugify(devdoc.source_file.replace(".md", ""))
            if devdoc.source_file
            else devdoc.slug
        )
        if not slug:
            continue

        document, created = Document.objects.get_or_create(
            slug=slug,
            defaults={
                "title": devdoc.title,
                "content": devdoc.content,
                "source": "devdoc",
                "source_type": "markdown",
                "metadata": {"devdoc_id": str(devdoc.id)},
            },
        )
        link_document_to_devdoc(devdoc, document)
        create_summary_from_doc(document)
        status = "Created" if created else "Exists"
        print(f"📄 {status}: {devdoc.title} → {slug}")
        if created:
            count += 1

    print(f"\n✅ Created {count} new Document records from DevDocs.")


if __name__ == "__main__":
    run()
