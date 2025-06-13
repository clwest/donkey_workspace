# mcp_core/dev_scripts/retry_failed_reflections.py

import os
import django
import sys

# Django setup
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
django.setup()

from django.db.models import Exists, OuterRef
from mcp_core.models import DevDoc
from intel_core.models import Document
from memory.models import MemoryEntry
from mcp_core.utils.devdoc_tools import link_document_to_devdoc, create_summary_from_doc


def run():
    from mcp_core.utils.devdoc_reflection import reflect_on_devdoc

    # Only DevDocs that are linked AND don't already have reflections
    reflections = MemoryEntry.objects.filter(
        document=OuterRef("linked_document"), type="reflection"
    )
    failed_docs = (
        DevDoc.objects.filter(linked_document__isnull=False)
        .annotate(has_reflection=Exists(reflections))
        .filter(has_reflection=False)
    )

    print(f"🔁 Retrying {failed_docs.count()} failed reflections...\n")

    for doc in failed_docs:
        print(f"🤔 Retrying: {doc.title}")
        if not doc.linked_document:
            possible = Document.objects.filter(slug=doc.slug).first()
            if possible:
                link_document_to_devdoc(doc, possible)
                create_summary_from_doc(possible)
        try:
            memory = reflect_on_devdoc(doc)
            if memory:
                print(f"✅ Saved memory: {memory.id}")
            else:
                print(f"⚠️ Skipped {doc.title} - no linked document")
        except Exception as e:
            print(f"❌ Error while reflecting on {doc.title}: {e}")


if __name__ == "__main__":
    run()
