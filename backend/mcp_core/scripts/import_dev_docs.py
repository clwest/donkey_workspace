import os
import sys
import django

# 🧠 Setup Django settings
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
sys.path.append(BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
django.setup()

from mcp_core.models import DevDoc
from django.utils.text import slugify
# 📁 Fix the docs dir path
DOCS_DIR = os.path.join(BASE_DIR, "docs")

def import_markdown_docs():
    if not os.path.exists(DOCS_DIR):
        print(f"❌ DOCS_DIR not found: {DOCS_DIR}")
        return

    for filename in os.listdir(DOCS_DIR):
        if not filename.endswith(".md"):
            continue

        filepath = os.path.join(DOCS_DIR, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        title = filename.replace(".md", "").replace("-", " ").title()
        slug = slugify(title)
        if len(slug) > 50:
            slug = slug[:50] 
            
        print(f"🔧 Truncated slug to fit DB: {slug}")
        doc, created = DevDoc.objects.update_or_create(
            slug=slug, defaults={"title": title, "content": content}
        )

        print(f"{'✅ Created' if created else '♻️ Updated'}: {filename}")


if __name__ == "__main__":
    import_markdown_docs()