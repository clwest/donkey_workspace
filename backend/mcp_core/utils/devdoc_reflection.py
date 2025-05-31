import os
import django
import sys

# Setup Django
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
django.setup()

import json
import logging

from django.utils.text import slugify
from memory.models import MemoryEntry
from mcp_core.models import DevDoc, Tag, GroupedDevDocReflection
from embeddings.helpers.helper_tagging import generate_tags_for_memory
from assistants.utils.assistant_reflection_engine import AssistantReflectionEngine
from utils.llm_router import call_llm
from django.utils import timezone

logger = logging.getLogger(__name__)


def reflect_on_devdoc(doc: DevDoc) -> MemoryEntry:
    if not doc.content:
        raise ValueError("DevDoc has no content.")

    assistant = AssistantReflectionEngine.get_reflection_assistant()
    engine = AssistantReflectionEngine(assistant=assistant)

    prompt = f"""
You are the Reflection Engine. Your job is to study internal dev documentation and summarize the most important architectural ideas, memory-worthy decisions, or potential improvements.

Analyze this document and summarize your insights as a system memory log:

--- DOCUMENT START ---
Title: {doc.title}

{doc.content}
--- DOCUMENT END ---
"""

    response = call_llm([
        {"role": "user", "content": prompt}
    ])

    if not response or len(response.strip()) < 10:
        raise ValueError("Empty or invalid reflection response")

    raw_tags = generate_tags_for_memory(response)
    tag_objs = []

    for tag in raw_tags:
        try:
            name = tag.lower().strip()
            slug = slugify(name)
            tag_obj, _ = Tag.objects.get_or_create(slug=slug, defaults={"name": name})
            tag_objs.append(tag_obj)
        except Exception as e:
            print(f"⚠️ Failed to create or fetch tag '{tag}': {e}")

    if not doc.linked_document:
        from intel_core.models import Document

        # Try to auto link by slug first, then by partial title match
        match = Document.objects.filter(slug=doc.slug).first()
        if not match:
            match = Document.objects.filter(title__icontains=doc.title).first()

        if match:
            doc.linked_document = match
            doc.save(update_fields=["linked_document"])
            logger.info(
                f"🔗 Auto-linked DevDoc '{doc.title}' to Document '{match.title}'"
            )
        else:
            logger.info(
                f"📄 No existing Document for DevDoc '{doc.title}'. Creating one"
            )
            match = Document.objects.create(
                title=doc.title,
                content=doc.content,
                source="devdoc",
            )
            doc.linked_document = match
            doc.save(update_fields=["linked_document"])
            logger.info(
                f"✅ Created Document '{match.title}' for DevDoc '{doc.title}'"
            )

    memory = MemoryEntry.objects.create(
        event=response.strip(),
        summary=f"Reflection on '{doc.title}'",
        assistant=assistant,
        type="reflection",
        document=doc.linked_document,
        source_role="assistant",
        source_user=None,
    )

    memory.tags.set(tag_objs)
    memory.save()
    
    doc.reflected_at = timezone.now()
    print(f"📌 Setting reflected_at for '{doc.title}' to {doc.reflected_at}")
    doc.save(update_fields=["reflected_at"])

    return memory



def summarize_and_group_devdocs() -> GroupedDevDocReflection:
    docs = DevDoc.objects.all()
    if not docs.exists():
        raise ValueError("No DevDocs found.")

    chunks = [
        f"Title: {doc.title}\nTags: {[t.name for t in doc.tags.all()]}\nSummary: {doc.content[:300]}..."
        for doc in docs
    ]

    prompt = f"""You are an AI developer assistant analyzing internal documentation.

Group the following documents into logical themes (3–7 clusters). For each group, return:
- A group title
- A group summary
- A list of related document titles
- Suggestions or TODOs

Use JSON format.

DEV DOCS:

{chr(10).join(chunks)}
"""

    assistant = AssistantReflectionEngine.get_reflection_assistant()
    response = call_llm([
        {"role": "user", "content": prompt}
    ])

    if not response or len(response.strip()) < 10:
        raise ValueError("LLM returned an empty or invalid response.")

    tags = generate_tags_for_memory(response)
    tag_objs = []
    for tag in tags:
        name = tag.lower().strip()
        slug = slugify(name)
        tag_obj, _ = Tag.objects.get_or_create(slug=slug, defaults={"name": name})
        tag_objs.append(tag_obj)

    # Parse related doc slugs
    related_doc_slugs = []
    try:
        parsed = json.loads(
            response.strip().strip("```json").strip("```").strip()
        )
        if isinstance(parsed, dict):
            groups = parsed.get("groups") or parsed.get("data") or []
        else:
            groups = parsed

        for group in groups:
            if not isinstance(group, dict):
                continue
            titles = group.get("related_document_titles", [])
            for title in titles:
                related_doc_slugs.append(slugify(title))
    except Exception as e:
        logger.warning(f"❌ Failed to parse related doc titles: {e}")

    related_docs = DevDoc.objects.filter(slug__in=related_doc_slugs)

    memory = MemoryEntry.objects.create(
        assistant=assistant,
        type="doc_group_summary",
        summary="Grouped summary of all current dev docs",
        event=response,
        source_role="assistant",
        document=None,
    )
    memory.tags.set(tag_objs)

    grouped = GroupedDevDocReflection.objects.create(
        summary=memory.summary,
        raw_json=response.strip(),
        source_assistant=assistant,
    )
    grouped.tags.set(tag_objs)
    grouped.related_docs.set(related_docs)

    return grouped