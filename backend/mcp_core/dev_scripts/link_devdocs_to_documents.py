# mcp_core/dev_scripts/link_devdocs_to_documents.py

import os
import django
import sys

# Setup Django
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
django.setup()

# mcp_core/dev_scripts/link_devdocs_to_documents.py

from mcp_core.models import DevDoc
from intel_core.models import Document
from django.utils.text import slugify
from difflib import get_close_matches

print("🔗 Linking DevDocs to Documents...")

for devdoc in DevDoc.objects.all():
    slug = slugify(devdoc.title)
    document = Document.objects.filter(slug=slug).first()

    if document:
        devdoc.document = document
        devdoc.save()
        print(f"✅ Linked: {devdoc.title} → {document.slug}")
    else:
        print(f"❌ No match for DevDoc: {devdoc.title} (→ {slug})")
        slugs = list(Document.objects.values_list("slug", flat=True))
        print(f"   🧐 Close matches: {get_close_matches(slug, slugs)}")