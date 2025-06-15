from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import logging
import json

from assistants.models.assistant import Assistant
from assistants.models.project import AssistantProject, AssistantReflectionLog
from assistants.utils.assistant_reflection_engine import (
    AssistantReflectionEngine,
    evaluate_thought_continuity,
)
from assistants.models.assistant import DelegationEvent
from assistants.models.thoughts import AssistantThoughtLog
from memory.models import MemoryEntry
from assistants.models.reflection import ReflectionGroup
from assistants.utils.reflection_summary import summarize_reflections_for_document


@api_view(["POST"])
@permission_classes([AllowAny])
def evaluate_continuity(request, slug):
    assistant = get_object_or_404(Assistant, slug=slug)
    project_id = request.data.get("project_id")
    project = None
    if project_id:
        project = get_object_or_404(AssistantProject, id=project_id)
    engine = AssistantReflectionEngine(assistant)
    result = evaluate_thought_continuity(engine, project=project)
    return Response(result)


@api_view(["GET"])
def subagent_reflect_view(request, event_id):
    """Return reflection on a delegated assistant's recent output."""
    event = (
        DelegationEvent.objects.select_related("child_assistant")
        .filter(id=event_id)
        .first()
    )
    if not event or not event.child_assistant:
        return Response({"error": "Delegation event not found"}, status=404)

    thoughts = list(
        AssistantThoughtLog.objects.filter(assistant=event.child_assistant).order_by(
            "-created_at"
        )[:5]
    )

    if not thoughts:
        return Response({"summary": "No sub-agent output found."})

    summary = " | ".join(t.thought[:50] for t in thoughts)

    return Response(
        {
            "summary": summary,
            "linked_thoughts": [t.thought for t in thoughts],
            "assistant_slug": event.child_assistant.slug,
        }
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def reflect_on_self(request, slug):
    """Generate a self reflection for an assistant and update identity."""
    assistant = get_object_or_404(Assistant, slug=slug)
    engine = AssistantReflectionEngine(assistant)
    prompt = (
        f"You are {assistant.name}. Reflect on your recent behavior and suggest"
        " updates to your persona_summary, traits, motto or values if needed."
        " Respond with a short reflection followed by a JSON object of updates."
    )

    output = engine.generate_reflection(prompt)
    text = output
    updates = {}
    if "{" in output:
        try:
            json_part = output[output.index("{") : output.rindex("}") + 1]
            text = output[: output.index("{")].strip()
            updates = json.loads(json_part)
        except Exception:
            pass

    if "#reflection-scope" not in text:
        text += "\n#reflection-scope:complete"

    AssistantReflectionLog.objects.create(
        assistant=assistant,
        summary=text,
        title="Self Reflection",
        category="self_reflection",
        raw_prompt=prompt,
    )

    if MemoryEntry.objects.filter(assistant=assistant, type="delegation").exists():
        if "delegation" not in text.lower():
            logging.getLogger(__name__).warning(
                "Delegation memories were not summarized"
            )

    if updates:
        if updates.get("persona_summary"):
            assistant.persona_summary = updates["persona_summary"]
        if updates.get("traits"):
            assistant.traits = updates["traits"]
        if updates.get("personality_description"):
            assistant.personality_description = updates["personality_description"]
        if updates.get("persona_mode"):
            assistant.persona_mode = updates["persona_mode"]
        if updates.get("values") is not None:
            assistant.values = updates["values"]
        if updates.get("motto"):
            assistant.motto = updates["motto"]
        assistant.save()

    return Response({"summary": text, "updates": updates})


@api_view(["GET"])
@permission_classes([AllowAny])
def recent_reflection_logs(request, slug):
    """Return the 10 most recent reflection logs for an assistant."""
    assistant = get_object_or_404(Assistant, slug=slug)
    logs = AssistantReflectionLog.objects.filter(assistant=assistant).order_by(
        "-created_at"
    )[:10]
    data = []
    for r in logs:
        data.append(
            {
                "id": str(r.id),
                "summary": r.summary,
                "document_title": r.document.title if r.document else None,
                "group_slug": r.group_slug,
                "is_summary": r.is_summary,
                "created_at": r.created_at.isoformat(),
            }
        )
    return Response(data)


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def reflection_group_list(request, slug):
    assistant = get_object_or_404(Assistant, slug=slug)
    if request.method == "POST":
        slug_val = request.data.get("slug")
        title = request.data.get("title", slug_val)
        if not slug_val:
            return Response({"error": "slug required"}, status=400)
        group, _ = ReflectionGroup.objects.get_or_create(
            assistant=assistant, slug=slug_val, defaults={"title": title}
        )
        return Response({"slug": group.slug, "title": group.title})

    groups = ReflectionGroup.objects.filter(assistant=assistant)
    from assistants.serializers import ReflectionGroupSerializer

    data = ReflectionGroupSerializer(groups, many=True).data
    return Response(data)


@api_view(["POST"])
@permission_classes([AllowAny])
def summarize_reflection_group(request):
    slug = request.data.get("slug")
    assistant_slug = request.data.get("assistant")
    if not slug or not assistant_slug:
        return Response({"error": "slug and assistant required"}, status=400)
    assistant = get_object_or_404(Assistant, slug=assistant_slug)
    group = get_object_or_404(ReflectionGroup, assistant=assistant, slug=slug)
    summarize_reflections_for_document(group_slug=slug, assistant_id=assistant.id)
    group.refresh_from_db()
    return Response({"summary": group.summary})


@api_view(["PATCH"])
@permission_classes([AllowAny])
def assign_reflection_group(request, id):
    reflection = get_object_or_404(AssistantReflectionLog, id=id)
    slug = request.data.get("group")
    if not slug:
        reflection.group_slug = None
        reflection.save(update_fields=["group_slug"])
        return Response({"group": None})

    group, _ = ReflectionGroup.objects.get_or_create(
        assistant=reflection.assistant,
        slug=slug,
        defaults={"title": slug},
    )
    reflection.group_slug = slug
    reflection.save(update_fields=["group_slug"])
    group.reflections.add(reflection)
    if reflection.document:
        group.documents.add(reflection.document)
        group.document_count = group.documents.count()
    group.save(update_fields=["document_count"])
    return Response({"group": slug})
