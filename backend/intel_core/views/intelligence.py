import json
import re
import traceback
import uuid
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from openai import OpenAI
from intel_core.models import (
    Document,
    DocumentSet,
    GlossaryMissReflectionLog,
    GlossaryFallbackReflectionLog,
)
from prompts.models import Prompt
from assistants.models.assistant import Assistant
from assistants.utils.assistant_thought_engine import AssistantThoughtEngine
from assistants.models.project import AssistantProject, AssistantObjective
from assistants.models.thoughts import AssistantThoughtLog
from prompts.utils.token_helpers import count_tokens, smart_chunk_prompt
from assistants.utils.chunk_retriever import get_relevant_chunks, ANCHOR_BOOST
from memory.models import MemoryEntry
from mcp_core.models import NarrativeThread, Tag


client = OpenAI()


def is_valid_uuid(value: str) -> bool:
    """Return True if the given value is a valid UUID string."""
    try:
        uuid.UUID(str(value))
        return True
    except (ValueError, TypeError):
        return False


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def summarize_with_context(request, pk):
    try:
        document = Document.objects.get(pk=pk)
    except Document.DoesNotExist:
        return Response({"error": "Document not found"}, status=404)

    text = document.content[:3000].strip()

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that summarizes technical documents.",
                },
                {"role": "user", "content": f"Summarize this document:\n\n{text}"},
            ],
            temperature=0.5,
            max_tokens=200,
        )
        summary = response.choices[0].message.content.strip()
        return Response({"summary": summary})
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(["POST"])
@permission_classes([AllowAny])
def summarize_document_with_context(request, pk):
    """Return an OpenAI summary using smart-chunked context."""
    text = request.data.get("text")
    document = None

    if not text:
        try:
            document = Document.objects.get(pk=pk)
            text = document.content
        except Document.DoesNotExist:
            return Response({"error": "Document not found"}, status=404)

    chunks = smart_chunk_prompt(text)
    sections = []
    token_total = 0
    for chunk in chunks:
        if token_total + chunk["tokens"] > 7000:
            break
        sections.append(chunk["section"])
        token_total += chunk["tokens"]

    prompt_text = "\n\n".join(sections).strip()

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that summarizes technical documents.",
                },
                {
                    "role": "user",
                    "content": f"Summarize this document:\n\n{prompt_text}",
                },
            ],
            temperature=0.5,
            max_tokens=200,
        )
        summary = response.choices[0].message.content.strip()
        return Response({"summary": summary})
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(["POST"])
@permission_classes([AllowAny])
def bootstrap_agent_from_docs(request, pk):
    try:
        document = Document.objects.get(pk=pk)
    except Document.DoesNotExist:
        return Response({"error": "Document not found"}, status=404)

    content = document.content[:6000].strip()
    user_prompt = f"""You are an assistant designed to help a user build an AI agent based on technical documentation.

Extract a proposed system prompt, assistant tone, key personality traits, and task specialties.

Technical Context:
{content}

Return only a JSON object with the fields: system_prompt, tone, personality, specialties."""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You generate structured assistant configurations from input text.",
                },
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.4,
            max_tokens=400,
        )
        return Response({"config": response.choices[0].message.content.strip()})
    except Exception as e:
        return Response({"error": str(e)}, status=500)


@api_view(["POST"])
@permission_classes([AllowAny])
def create_bootstrapped_assistant_from_document(request, pk):
    try:
        document = Document.objects.get(pk=pk)
    except Document.DoesNotExist:
        return Response(
            {"error": "Document not found"}, status=status.HTTP_404_NOT_FOUND
        )

    # If an assistant already exists for this document, reuse it
    existing = Assistant.objects.filter(documents=document).first()
    if existing:
        assistant_project = AssistantProject.objects.filter(assistant=existing).first()
        if not assistant_project:
            assistant_project = AssistantProject.objects.create(
                assistant=existing,
                title=f"{existing.name} - Project 1",
                description=f"Auto-generated project for {existing.name} based on document.",
            )
        objective = AssistantObjective.objects.filter(
            project=assistant_project, assistant=existing
        ).first()
        if not objective:
            objective = AssistantObjective.objects.create(
                project=assistant_project,
                assistant=existing,
                title="Understand core technologies",
                description="Explore key components from the linked documentation and prepare to assist users effectively.",
            )
        return Response(
            {
                "name": existing.name,
                "slug": existing.slug,
                "project_id": assistant_project.id if assistant_project else None,
                "memory_id": None,
                "thread_id": None,
                "objective_id": objective.id if objective else None,
            }
        )

    content = document.content[:6000].strip()

    bootstrap_prompt = f"""
You are an assistant designed to help a user build an AI assistant agent from technical documentation.

Extract the following fields:
- `name`: a concise, human-friendly assistant name (max 80 characters)
- `system_prompt`: detailed instructions for how the assistant should behave
- `tone`: one or two words describing tone
- `personality`: a short sentence or phrase about their vibe
- `specialties`: list of specific topics or skills

Documentation:
{content}

Return only JSON in this format:
{{
  "name": "...",
  "system_prompt": "...",
  "tone": "...",
  "personality": "...",
  "specialties": ["..."]
}}
"""

    try:
        print("📨 Sending prompt to OpenAI...")
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You generate assistant agent configs from documentation.",
                },
                {"role": "user", "content": bootstrap_prompt},
            ],
            temperature=0.4,
            max_tokens=500,
        )

        raw_response = response.choices[0].message.content.strip()
        print("🧾 Raw assistant config response:\n", raw_response)

        cleaned = re.sub(
            r"^```(?:json)?\s*|\s*```$", "", raw_response.strip(), flags=re.IGNORECASE
        )
        print(f"🧪 Cleaned JSON:\n{cleaned}")

        config = json.loads(cleaned)
        print("✅ Parsed assistant config")

        assistant_name = (config.get("name") or document.title).strip()[:80]

        print("📌 Saving system prompt...")
        sys_prompt = Prompt.objects.create(
            content=config["system_prompt"],
            type="system",
            tone=config.get("tone", "neutral"),
            token_count=count_tokens(config["system_prompt"]),
        )

        print("🤖 Saving assistant...")
        assistant = Assistant.objects.create(
            name=assistant_name,
            slug="bootstrap-" + str(uuid.uuid4())[:8],
            system_prompt=sys_prompt,
            tone=config.get("tone", "neutral"),
            personality=config.get("personality", "Helpful and curious."),
            specialty=", ".join(config.get("specialties", [])),
            is_demo=False,
        )

        assistant.save()
        assistant.documents.add(document)
        print("📎 Linked document to assistant")

        print("📁 Creating project...")
        assistant_project = AssistantProject.objects.create(
            assistant=assistant,
            title=f"{assistant.name} - Project 1",
            description=f"Auto-generated project for {assistant.name} based on document.",
        )

        print("🎯 Creating initial objective...")
        objective = AssistantObjective.objects.create(
            project=assistant_project,
            assistant=assistant,
            title="Understand core technologies",
            description="Explore key components from the linked documentation and prepare to assist users effectively.",
        )

        # Create and link a memory entry
        memory = MemoryEntry.objects.create(
            summary=f"Assistant '{assistant.name}' bootstrapped from document '{document.title}'",
            event=f"Assistant {assistant.name} created",
            assistant=assistant,
            document=document,
            type="event",
            auto_tagged=True,
        )

        # Optionally create a NarrativeThread linked to this
        thread = NarrativeThread.objects.create(
            title=f"{assistant.name} Bootstrap Thread",
            summary="Auto-generated thread for assistant setup and future reflections.",
        )
        thread.documents.add(document)
        thread.memories.add(memory)
        thread.save()

        # Auto-plan tasks for the first objective
        engine = AssistantThoughtEngine(assistant=assistant, project=assistant_project)
        engine.plan_tasks_from_objective(objective)

        AssistantThoughtLog.objects.create(
            assistant=assistant,
            thought_type="planning",
            thought=(
                f"I was created to assist with {document.title} based on the linked document."
            ),
        )

        print("✅ All components created")

        return Response(
            {
                "name": assistant.name,
                "slug": assistant.slug,
                "project_id": assistant_project.id,
                "memory_id": memory.id if memory else None,
                "thread_id": thread.id if thread else None,
                "objective_id": objective.id if objective else None,
            }
        )

    except Exception as e:
        print("❌ Error during assistant bootstrapping")
        print(traceback.format_exc())
        return Response(
            {
                "error": str(e),
                "trace": traceback.format_exc(),
            },
            status=500,
        )


@api_view(["POST"])
@permission_classes([AllowAny])
def create_assistant_from_document_set(request, pk):
    """Bootstrap an assistant using a DocumentSet."""
    try:
        doc_set = DocumentSet.objects.get(pk=pk)
    except DocumentSet.DoesNotExist:
        return Response({"error": "DocumentSet not found"}, status=404)

    first_doc = doc_set.documents.first()
    if not first_doc:
        return Response({"error": "DocumentSet has no documents"}, status=400)

    return create_bootstrapped_assistant_from_document(request, first_doc.id)


@api_view(["POST"])
@permission_classes([AllowAny])
def rag_check_source(request):
    """Return top matching document chunks for the provided text."""

    assistant_id = request.data.get("assistant_id")
    content = request.data.get("content")
    mode = request.data.get("mode", "response")

    assistant = None
    if assistant_id:
        from utils.resolvers import resolve_or_error
        from django.core.exceptions import ObjectDoesNotExist

        try:
            assistant = resolve_or_error(assistant_id, Assistant)
        except ObjectDoesNotExist:
            assistant = None

    if not content:
        return Response({"error": "content is required"}, status=400)

    (
        chunks,
        reason,
        fallback,
        glossary_present,
        top_score,
        _,
        glossary_forced,
        _,
        _,
        debug_info,
    ) = get_relevant_chunks(
        assistant_id if assistant else None,
        content,
        memory_context_id=str(assistant.memory_context_id) if assistant else None,
    )
    debug = {
        "fallback": fallback,
        "reason": reason,
        "glossary_present": glossary_present,
        "retrieval_score": top_score,
        "anchor_boost": ANCHOR_BOOST,
        **debug_info,
    }
    return Response({"results": chunks, "mode": mode, "debug": debug})


@api_view(["GET"])
@permission_classes([AllowAny])
def glossary_misses(request):
    """Return logged glossary miss reflections."""
    anchor = request.query_params.get("anchor")
    logs = GlossaryMissReflectionLog.objects.all()
    if anchor:
        if is_valid_uuid(anchor):
            logs = logs.filter(anchor__id=anchor)
        else:
            logs = logs.filter(anchor__slug=anchor)
    data = []
    for log in logs.order_by("-created_at")[:50]:
        data.append(
            {
                "id": str(log.id),
                "question": log.user_question,
                "response": log.assistant_response,
                "reflection": log.reflection,
                "anchor": log.anchor.slug if log.anchor else None,
                "chunks": [str(c.id) for c in log.matched_chunks.all()],
            }
        )
    return Response({"results": data})


@api_view(["GET"])
@permission_classes([AllowAny])
def glossary_fallback_logs(request):
    """Return logs when glossary context was ignored."""
    anchor = request.query_params.get("anchor")
    logs = GlossaryFallbackReflectionLog.objects.all()
    if anchor:
        logs = logs.filter(anchor_slug=anchor)
    data = []
    for log in logs.order_by("-created_at")[:50]:
        data.append(
            {
                "slug": log.anchor_slug,
                "chunk_id": log.chunk_id,
                "score": log.match_score,
                "response": log.assistant_response,
                "injected": log.glossary_injected,
            }
        )
    return Response({"results": data})
