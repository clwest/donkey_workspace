from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import json
from openai import OpenAI

from assistants.models import Assistant, AssistantThoughtLog
from memory.services import MemoryService
from intel_core.models import Document

client = OpenAI()


@api_view(["POST"])
@permission_classes([AllowAny])
def diff_knowledge(request, slug):
    """Compare assistant prompt + memories with new text."""
    assistant = get_object_or_404(Assistant, slug=slug)

    doc_id = request.data.get("document_id")
    reflection = request.data.get("reflection")
    text = request.data.get("text")

    if not any([doc_id, reflection, text]):
        return Response(
            {"error": "Provide document_id, reflection, or text"}, status=400
        )

    if doc_id:
        doc = get_object_or_404(Document, id=doc_id)
        source_text = f"{doc.title}\n\n{doc.content or ''}"
    elif reflection:
        source_text = reflection
    else:
        source_text = text

    prompt_content = assistant.system_prompt.content if assistant.system_prompt else ""
    thoughts = AssistantThoughtLog.objects.filter(assistant=assistant).order_by("-created_at")[:5]
    thought_text = "\n".join(t.thought for t in thoughts if t.thought)
    memories = MemoryService.filter_entries(assistant=assistant).order_by("-timestamp")[:5]
    memory_text = "\n".join(m.summary or m.event for m in memories if m.summary or m.event)

    context = (
        f"System Prompt:\n{prompt_content}\n\n"
        f"Recent Memories:\n{memory_text}\n\n"
        f"Recent Thoughts:\n{thought_text}"
    )

    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0.3,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You analyze how well an assistant's prompt and memories align "
                        "with new information. Return JSON with keys diff_summary, "
                        "prompt_updates, and tone_suggestions."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Current knowledge:\n{context}\n\nNew text:\n{source_text}",
                },
            ],
        )
        content = completion.choices[0].message.content.strip()
        result = json.loads(content)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

    return Response(result)
