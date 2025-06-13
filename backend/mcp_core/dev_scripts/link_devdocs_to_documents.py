# mcp_core/dev_scripts/link_devdocs_to_documents.py
import os
import sys
import django
from django.utils.text import slugify
from difflib import get_close_matches

# Setup Django
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
django.setup()

from mcp_core.models import DevDoc
from intel_core.models import Document
from mcp_core.utils.devdoc_tools import link_document_to_devdoc, create_summary_from_doc

print("🔗 Linking DevDocs to Documents...")
linked = 0
missing = []

for devdoc in DevDoc.objects.all():
    slug = slugify(devdoc.title)
    document = (
        Document.objects.filter(slug=slug).first()
        or Document.objects.filter(title__iexact=devdoc.title.strip()).first()
    )
    if document:
        link_document_to_devdoc(devdoc, document)
        create_summary_from_doc(document)
        linked += 1
        print(f"✅ Linked: {devdoc.title} → {document.slug}")
    else:
        missing.append(devdoc.slug)
        print(f"❌ No match for DevDoc: {devdoc.title} (→ {slug})")
        slugs = list(Document.objects.values_list("slug", flat=True))
        print(f"   🧐 Close matches: {get_close_matches(slug, slugs)}")

print(f"\nLinked {linked} DevDocs")
if missing:
    print(f"Missing documents for: {', '.join(missing)}")
