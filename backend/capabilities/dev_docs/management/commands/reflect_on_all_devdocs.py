import os
import django
import sys

# Setup Django
sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.."))
)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
django.setup()

# mcp_core/dev_scripts/reflect_on_all_devdocs.py

from django.utils.text import slugify
from intel_core.models import Document
from assistants.models import Assistant
from assistants.utils.core_assistant import CoreAssistant

print("🧠 Reflecting on all DevDocs...")

# Use your reflection assistant — adjust slug as needed
try:
    zeno = Assistant.objects.get(slug="zeno-the-build-wizard")
except Assistant.DoesNotExist:
    print("❌ Assistant 'zeno-the-build-wizard' not found.")
    exit()

docs = Document.objects.all()
for doc in docs:
    title = doc.title
    slug = slugify(title)

    if not doc.content or len(doc.content.strip()) < 20:
        print(f"⚠️ Skipping: {title} — too short")
        continue

    try:
        assistant = CoreAssistant(assistant=zeno)
        summary, insights = assistant.reflect_on_doc(doc)
        print(f"✅ Reflected on: {title}")
    except Exception as e:
        print(f"❌ Error while reflecting on {title}: {e}")