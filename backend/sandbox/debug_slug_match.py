import os
import django
import sys

# Django setup
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
django.setup()

from mcp_core.models import DevDoc
from intel_core.models import Document

print("🧪 DevDoc.source_file vs Document.slug comparison\n")

all_doc_slugs = set(Document.objects.values_list("slug", flat=True))
print(f"📚 {len(all_doc_slugs)} document slugs loaded.")

for devdoc in DevDoc.objects.all():
    source = (devdoc.source_file or "").replace(".md", "").strip()
    if not source:
        continue

    match = source in all_doc_slugs
    closest = [slug for slug in all_doc_slugs if slug.startswith(source[:5])]
    print(f"📄 DevDoc: {devdoc.title}")
    print(f"   → Looking for: `{source}`")
    print(f"   → Match found: {match}")
    if not match:
        print(f"   🧭 Closest slug(s): {closest[:3]}")
    print("—" * 40)
