import os
import django
import sys


# Setup Django
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
django.setup()

from django.utils.text import slugify
from intel_core.models import Document


def generate_unique_slug(base_slug, existing_slugs):
    """
    Ensure the slug is unique among existing slugs.
    """
    slug = base_slug[:90]  # Reserve room for suffixes
    count = 2
    while slug in existing_slugs:
        suffix = f"-{count}"
        slug = (base_slug[:90 - len(suffix)] + suffix)
        count += 1
    return slug


def run():
    docs = Document.objects.filter(slug__isnull=True) | Document.objects.filter(slug="")
    print(f"📄 Found {docs.count()} documents missing slugs")

    existing_slugs = set(
        Document.objects.exclude(slug__isnull=True).exclude(slug="").values_list("slug", flat=True)
    )

    updated = 0
    for doc in docs:
        base_slug = slugify(doc.title)
        if not base_slug:
            base_slug = "doc"

        unique_slug = generate_unique_slug(base_slug, existing_slugs)
        doc.slug = unique_slug
        doc.save()
        existing_slugs.add(unique_slug)
        updated += 1
        print(f"✅ Slug set: {unique_slug}")

    print(f"\n🔁 Backfilled slugs for {updated} documents")


if __name__ == "__main__":
    run()