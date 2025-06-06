from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from assistants.models.reflection import (
    AssistantReflectionInsight,
    AssistantReflectionLog,
)
from assistants.models.assistant import Assistant
from assistants.models.project import AssistantMemoryChain
from assistants.models.thoughts import AssistantThoughtLog
from assistants.serializers import (
    AssistantMemoryChainSerializer,
    AssistantReflectionInsightSerializer,
    AssistantReflectionLogSerializer,
    AssistantReflectionLogListSerializer,
    AssistantReflectionLogDetailSerializer,
    AssistantThoughtLogSerializer,
    ReflectionReplayLogSerializer,
)
from project.models import ProjectMemoryLink
from capabilities.utils import log_capability_usage
from project.serializers import ProjectMemoryLinkSerializer

from memory.services import MemoryService
from memory.models import ReflectionReplayLog
from memory.serializers import (
    MemoryEntrySerializer,
    MemoryEntrySlimSerializer,
    PrioritizedMemorySerializer,
    SimulatedMemoryForkSerializer,
)
from memory.utils import replay_reflection as replay_reflection_util
from utils.similarity.compare_reflections import compare_reflections
from assistants.utils.assistant_reflection_engine import AssistantReflectionEngine
from assistants.utils.memory_filters import get_filtered_memories
from assistants.helpers.reflection_helpers import simulate_memory_fork
from intel_core.models import Document
from assistants.services import AssistantService


# Assistant Memory Chains
@api_view(["GET", "POST", "PATCH"])
def assistant_memory_chains(request, project_id):
    if request.method == "GET":
        chains = AssistantMemoryChain.objects.filter(project_id=project_id)
        serializer = AssistantMemoryChainSerializer(chains, many=True)
        return Response(serializer.data)
    if request.method == "POST":
        serializer = AssistantMemoryChainSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(project_id=project_id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    if request.method == "PATCH":
        chain_id = request.data.get("id")
        chain = get_object_or_404(
            AssistantMemoryChain, id=chain_id, project_id=project_id
        )
        serializer = AssistantMemoryChainSerializer(
            chain, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PATCH"])
def assistant_memory_chain_detail(request, chain_id):
    chain = get_object_or_404(AssistantMemoryChain, id=chain_id)
    serializer = AssistantMemoryChainSerializer(chain, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def linked_memories(request, project_id):
    links = ProjectMemoryLink.objects.filter(project_id=project_id)
    serializer = ProjectMemoryLinkSerializer(links, many=True)
    return Response(serializer.data)


@api_view(["POST"])
def link_memory_to_project(request):
    serializer = ProjectMemoryLinkSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Assistant Reflection Insights
@api_view(["GET"])
def assistant_project_reflections(request, project_id):
    reflections = AssistantReflectionLog.objects.filter(project_id=project_id).order_by(
        "-created_at"
    )
    serializer = AssistantReflectionLogSerializer(reflections, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def assistant_memories(request, slug):
    """List memory entries for a specific assistant."""
    assistant = get_object_or_404(Assistant, slug=slug)
    entries = MemoryService.filter_entries(assistant=assistant)
    if assistant.current_project_id:
        entries = entries.filter(related_project_id=assistant.current_project_id)

    symbolic_change = request.GET.get("symbolic_change")
    campaign_id = request.GET.get("campaign_id")

    if symbolic_change in ["true", "1", "yes"]:
        entries = entries.filter(symbolic_change=True)
    if campaign_id:
        entries = entries.filter(related_campaign_id=campaign_id)
    entries = entries.order_by("-created_at")
    serializer = MemoryEntrySlimSerializer(entries, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def prioritized_memories(request, slug):
    """Return prioritized memories for the assistant."""
    assistant = get_object_or_404(Assistant, slug=slug)
    task = request.GET.get("task")
    project = assistant.current_project
    from assistants.helpers.memory_helpers import get_relevant_memories_for_task

    memories = get_relevant_memories_for_task(
        assistant,
        project=project,
        task_type=task,
        limit=10,
    )
    serializer = PrioritizedMemorySerializer(memories, many=True)
    return Response(serializer.data)


@api_view(["POST"])
def reflect_now(request, slug):
    """Trigger an immediate reflection using optional context."""
    assistant = get_object_or_404(Assistant, slug=slug)

    log_capability_usage(request, "can_run_reflection")

    memory_id = request.data.get("memory_id")
    project_id = request.data.get("project_id")
    doc_id = request.data.get("doc_id")

    if memory_id:
        memory = MemoryService.get_entry_or_404(memory_id)
        if not memory.context:
            memory.context = assistant.memory_context
            memory.save(update_fields=["context"])
    elif project_id or doc_id:
        # legacy parameters ignored; reflections use assistant.memory_context
        pass

    engine = AssistantReflectionEngine(assistant)
    ref_log = engine.reflect_now()
    if not ref_log:
        return Response({"status": "skipped", "summary": ""})
    return Response({"status": "ok", "summary": ref_log.summary})


@api_view(["POST"])
def reflect_on_memory_chain(request, slug):
    """Run reflection on a specific memory chain."""
    assistant = get_object_or_404(Assistant, slug=slug)
    chain_id = request.data.get("chain_id")
    chain = get_object_or_404(AssistantMemoryChain, id=chain_id)

    memories = get_filtered_memories(chain)
    texts = [m.event.strip() for m in memories if m.event]
    if not texts:
        return Response({"summary": "No relevant memories."})

    engine = AssistantReflectionEngine(assistant)
    prompt = engine.build_reflection_prompt(texts)
    summary = engine.generate_reflection(prompt)
    AssistantReflectionLog.objects.create(
        assistant=assistant,
        project=chain.project,
        title=f"Reflection on {chain.title}",
        summary=summary,
        raw_prompt=prompt,
    )
    return Response({"summary": summary})


@api_view(["GET"])
def assistant_reflection_logs(request, slug):
    """List all reflection logs for an assistant."""
    assistant = get_object_or_404(Assistant, slug=slug)
    reflections = AssistantReflectionLog.objects.filter(assistant=assistant)
    if assistant.current_project_id:
        reflections = reflections.filter(project_id=assistant.current_project_id)
    reflections = reflections.order_by("-created_at")
    serializer = AssistantReflectionLogListSerializer(reflections, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def assistant_reflection_detail(request, id):
    """Retrieve full reflection log details."""
    reflection = get_object_or_404(AssistantReflectionLog, id=id)
    serializer = AssistantReflectionLogDetailSerializer(reflection)
    return Response(serializer.data)


@api_view(["GET"])
def reflection_thoughts(request, id):
    """Return thoughts linked to a specific reflection."""
    thoughts = AssistantThoughtLog.objects.filter(linked_reflection_id=id).order_by(
        "-created_at"
    )
    serializer = AssistantThoughtLogSerializer(thoughts, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def assistant_reflection_replays(request, slug):
    """List reflection replay logs for an assistant."""
    assistant = get_object_or_404(Assistant, slug=slug)
    replays = ReflectionReplayLog.objects.filter(assistant=assistant).order_by("-created_at")
    serializer = ReflectionReplayLogSerializer(replays, many=True)
    return Response(serializer.data)


@api_view(["POST"])
def replay_reflection(request, id):
    """Replay a reflection with updated glossary anchors."""
    reflection = get_object_or_404(AssistantReflectionLog, id=id)
    replay = replay_reflection_util(reflection)
    serializer = ReflectionReplayLogSerializer(replay)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def reflection_replay_diff(request, slug, id):
    """Return diff stats for a reflection replay."""
    assistant = get_object_or_404(Assistant, slug=slug)
    replay = get_object_or_404(ReflectionReplayLog, id=id, assistant=assistant)

    original = replay.original_reflection.summary if replay.original_reflection else ""
    replayed = replay.replayed_summary

    diff = compare_reflections(original, replayed)
    diff.update({"original": original, "replayed": replayed, "status": replay.status, "drift_reason": replay.drift_reason})
    return Response(diff)


@api_view(["GET"])
def rag_playback_detail(request, slug, id):
    """Return RAG playback metadata for a replay."""
    assistant = get_object_or_404(Assistant, slug=slug)
    from memory.models import RAGPlaybackLog

    playback = get_object_or_404(RAGPlaybackLog, id=id, assistant=assistant)
    from memory.serializers import RAGPlaybackLogSerializer

    data = RAGPlaybackLogSerializer(playback).data
    return Response(data)


@api_view(["POST"])
def accept_replay(request, id):
    """Accept a replay and update the original reflection."""
    replay = get_object_or_404(ReflectionReplayLog, id=id)
    if replay.original_reflection and replay.replayed_summary:
        replay.original_reflection.summary = replay.replayed_summary
        replay.original_reflection.save(update_fields=["summary"])
    replay.status = ReflectionReplayLog.ReplayStatus.ACCEPTED
    replay.save(update_fields=["status"])
    return Response({"status": "accepted"})


@api_view(["POST"])
def reject_replay(request, id):
    """Reject a replay."""
    replay = get_object_or_404(ReflectionReplayLog, id=id)
    replay.status = ReflectionReplayLog.ReplayStatus.SKIPPED
    replay.save(update_fields=["status"])
    return Response({"status": "skipped"})


@api_view(["GET"])
def assistant_memory_summary(request, slug):
    """Return a summary of recent memories for the assistant."""
    assistant = get_object_or_404(Assistant, slug=slug)

    qs = MemoryService.filter_entries(assistant=assistant)
    if assistant.current_project_id:
        qs = qs.filter(related_project_id=assistant.current_project_id)

    total = qs.count()
    recent = list(qs.order_by("-created_at")[:30])

    from collections import Counter

    tag_counter = Counter()
    mood_counter = Counter()
    recent_list = []

    for mem in recent:
        tags = list(mem.tags.values_list("slug", flat=True))
        for t in tags:
            tag_counter[t] += 1
        if mem.emotion:
            mood_counter[mem.emotion.lower()] += 1
        recent_list.append(
            {
                "id": str(mem.id),
                "summary": mem.summary or (mem.event[:80] if mem.event else ""),
                "tags": tags,
                "mood": mem.emotion or "",
                "created_at": mem.created_at.isoformat().replace("+00:00", "Z"),
            }
        )

    return Response(
        {
            "total": total,
            "recent_tags": dict(tag_counter),
            "recent_moods": dict(mood_counter),
            "most_recent": recent_list,
        }
    )


@api_view(["POST"])
def simulate_memory(request, slug):
    """Create a simulated memory fork."""
    assistant = get_object_or_404(Assistant, slug=slug)
    memory_id = request.data.get("memory_id")
    if not memory_id:
        return Response({"error": "memory_id required"}, status=400)

    memory = MemoryService.get_entry_or_404(memory_id)
    action = request.data.get("alternative_action")
    notes = request.data.get("notes")

    fork = simulate_memory_fork(assistant, memory, action, notes)
    serializer = SimulatedMemoryForkSerializer(fork)
    return Response(serializer.data, status=201)


@api_view(["GET"])
def assistant_memory_documents(request, slug):
    """List documents currently loaded in memory for an assistant."""
    assistant = get_object_or_404(Assistant, slug=slug)

    doc_ids = set(assistant.documents.values_list("id", flat=True))

    doc_ids.update(
        MemoryService.filter_entries(
            assistant=assistant, document_id__isnull=False
        ).values_list("document_id", flat=True)
    )

    doc_ids.update(
        AssistantReflectionLog.objects.filter(
            assistant=assistant,
            linked_memory__document_id__isnull=False,
        ).values_list("linked_memory__document_id", flat=True)
    )

    doc_ids.update(
        AssistantReflectionInsight.objects.filter(assistant=assistant).values_list(
            "linked_document_id", flat=True
        )
    )

    doc_ids.update(
        MemoryService.filter_entries(
            assistantmemorychain__project__assistant=assistant,
            document_id__isnull=False,
        ).values_list("document_id", flat=True)
    )

    documents = Document.objects.filter(id__in=doc_ids).distinct()

    from intel_core.helpers.document_helpers import get_document_memory_status

    data = [get_document_memory_status(doc) for doc in documents]
    return Response(data)
