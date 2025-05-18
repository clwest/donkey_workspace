
from rest_framework.decorators import api_view
from rest_framework.response import Response
from mcp_core.models import DevDoc, Tag
from memory.models import MemoryEntry
from django.utils.text import slugify
from embeddings.helpers.helper_tagging import generate_tags_for_memory
from assistants.utils.assistant_reflection_engine import AssistantReflectionEngine
from utils.llm import call_gpt4


@api_view(["POST"])
def summarize_and_group_devdocs(request):
    docs = DevDoc.objects.all()
    if not docs.exists():
        return Response({"error": "No DevDocs found."}, status=404)

    chunks = []
    for doc in docs:
        chunks.append(f"""Title: {doc.title}\nTags: {[t.name for t in doc.tags.all()]}\nSummary: {doc.content[:300]}...\n""")

    prompt = f"""You are an AI developer assistant analyzing internal documentation.

Group the following documents into logical themes (3-7 clusters). For each group, return:
- A group title
- A group summary
- A list of related document titles
- Suggestions or TODOs

Use JSON format.
\n\nDEV DOCS:\n\n{chr(10).join(chunks)}"""

    assistant = AssistantReflectionEngine.get_reflection_assistant()
    response = call_gpt4(prompt)

    if not response or len(response.strip()) < 10:
        return Response({"error": "LLM returned an empty or invalid response."}, status=500)

    tags = generate_tags_for_memory(response)
    tag_objs = []

    for tag in tags:
        name = tag.lower().strip()
        slug = slugify(name)
        tag_obj, _ = Tag.objects.get_or_create(slug=slug, defaults={"name": name})
        tag_objs.append(tag_obj)

    memory = MemoryEntry.objects.create(
        assistant=assistant,
        type="doc_group_summary",
        summary="Grouped summary of all current dev docs",
        event=response,
        source_role="assistant",
        document=None,
    )
    memory.tags.set(tag_objs)
    memory.save()

    return Response({
        "summary": memory.summary,
        "event": memory.event,
        "tags": [t.name for t in tag_objs],
        "created_at": memory.created_at,
        "memory_id": memory.id,
    })
