from rest_framework.decorators import (
    api_view,
    permission_classes,
    parser_classes,
    action,
)
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.pagination import PageNumberPagination
from django.core.cache import cache
import uuid
import warnings
import logging

from django.conf import settings

from assistants.models import Assistant

from .models import (
    MemoryEntry,
    MemoryChain,
    MemoryFeedback,
    SharedMemoryPool,
    SharedMemoryEntry,
    BraidedMemoryStrand,
    ContinuityAnchorPoint,
    MemoryEmbeddingFailureLog,
    SymbolicMemoryAnchor,
    GlossaryRetryLog,
    GlossaryKeeperLog,
    AnchorConvergenceLog,
    AnchorReinforcementLog,
    AnchorSuggestion,
    ReflectionFlag,
)
from .serializers import (
    MemoryEntrySerializer,
    MemoryEntrySlimSerializer,
    MemoryFeedbackSerializer,
    MemoryChainSerializer,
    SharedMemoryPoolSerializer,
    SharedMemoryEntrySerializer,
    BraidedMemoryStrandSerializer,
    ContinuityAnchorPointSerializer,
    MemoryMergeSuggestionSerializer,
    SymbolicMemoryAnchorSerializer,
    GlossaryRetryLogSerializer,
    GlossaryKeeperLogSerializer,
    AnchorConvergenceLogSerializer,
    AnchorReinforcementLogSerializer,
    AnchorSuggestionSerializer,
)
from prompts.serializers import PromptSerializer
from prompts.models import Prompt
from django.utils import timezone
from openai import OpenAI
from core.services.memory_service import reflect_on_memory as service_reflect_on_memory
from dotenv import load_dotenv
from embeddings.helpers.helpers_io import save_embedding
from prompts.utils.mutation import mutate_prompt as run_mutation
from embeddings.helpers.helpers_io import get_embedding_for_text
from memory.memory_service import get_memory_service
from memory.utils.feedback_engine import apply_memory_feedback
from mcp_core.models import NarrativeThread
from memory.utils.thread_helpers import get_linked_chains, recall_from_thread
from memory.utils.anamnesis_engine import run_anamnesis_retrieval
from memory.services.reinforcement import reinforce_glossary_anchor
from memory.services.acquisition import update_anchor_acquisition
from memory.utils.reflection_replay import replay_reflection

load_dotenv()

client = OpenAI()
logger = logging.getLogger(__name__)


def _rate_limited(request, key: str, window: int = 3) -> bool:
    """Simple per-user rate limit using the cache."""
    ident = (
        request.user.id
        if request.user.is_authenticated
        else request.META.get("REMOTE_ADDR")
    )
    cache_key = f"rl:{ident}:{key}"
    if cache.get(cache_key):
        return True
    cache.set(cache_key, 1, timeout=window)
    return False


class MemoryEntryViewSet(viewsets.ModelViewSet):
    """ViewSet for CRUD operations on MemoryEntry."""

    queryset = MemoryEntry.objects.all().order_by("-created_at")
    serializer_class = MemoryEntrySerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["post"])
    def bookmark(self, request, pk=None):
        return bookmark_memory(request, memory_id=pk)

    @action(detail=True, methods=["post"])
    def unbookmark(self, request, pk=None):
        return unbookmark_memory(request, memory_id=pk)

    @action(detail=False, methods=["get"])  # /entries/bookmarked/
    def bookmarked(self, request):
        return bookmarked_memories(request)

    @action(detail=True, methods=["post"])
    def mutate(self, request, pk=None):
        return mutate_memory(request, id=pk)


class MemoryChainViewSet(viewsets.ModelViewSet):
    """ViewSet for MemoryChain resources."""

    queryset = MemoryChain.objects.all().order_by("-created_at")
    serializer_class = MemoryChainSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["get"])
    def summarize(self, request, pk=None):
        return summarize_chain_view(request, chain_id=pk)

    @action(detail=True, methods=["get"])
    def flowmap(self, request, pk=None):
        return chain_flowmap_view(request, chain_id=pk)

    @action(detail=True, methods=["get"], url_path="cross_project_recall")
    def cross_project_recall(self, request, pk=None):
        return cross_project_recall_view(request, chain_id=pk)


class MemoryFeedbackViewSet(viewsets.ModelViewSet):
    queryset = MemoryFeedback.objects.all().order_by("-created_at")
    serializer_class = MemoryFeedbackSerializer
    permission_classes = [IsAuthenticated]


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_memory_chain(request):
    warnings.warn(
        "Deprecated: use /api/v1/memory/chains/",
        DeprecationWarning,
    )
    title = request.data.get("title")
    memory_ids = request.data.get("memory_ids", [])

    if not title or not memory_ids:
        return Response({"error": "Missing title or memory IDs."}, status=400)

    memories = MemoryEntry.objects.filter(id__in=memory_ids)
    if not memories.exists():
        return Response({"error": "No valid memories found."}, status=400)

    chain = MemoryChain.objects.create(title=title)
    chain.memories.set(memories)

    return Response({"chain_id": chain.id, "title": chain.title})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_memory_chain(request, pk):
    try:
        chain = MemoryChain.objects.get(id=pk)
        serialized = {
            "id": str(chain.id),
            "title": chain.title,
            "memories": [
                {"id": str(m.id), "event": m.event} for m in chain.memories.all()
            ],
            "created_at": chain.created_at,
        }
        return Response(serialized)
    except MemoryChain.DoesNotExist:
        return Response({"error": "Chain not found"}, status=404)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_memory_chains(request):
    chains = MemoryChain.objects.all().order_by("-created_at")
    data = [
        {"id": str(chain.id), "title": chain.title, "created_at": chain.created_at}
        for chain in chains
    ]
    return Response(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def summarize_chain_view(request, chain_id):
    chain = get_object_or_404(MemoryChain, id=chain_id)
    from .utils.chain_helpers import summarize_memory_chain

    summary = summarize_memory_chain(chain)
    return Response({"chain_id": str(chain.id), "summary": summary})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def chain_flowmap_view(request, chain_id):
    chain = get_object_or_404(MemoryChain, id=chain_id)
    from .utils.chain_helpers import generate_flowmap_from_chain

    data = generate_flowmap_from_chain(chain)
    return Response(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def linked_chains_view(request, thread_id):
    thread = get_object_or_404(NarrativeThread, id=thread_id)
    chains = get_linked_chains(thread)
    serialized = []
    for chain in chains:
        projects = list(
            chain.memories.values_list("related_project__title", flat=True).distinct()
        )
        assistants = list(
            chain.memories.values_list("assistant__name", flat=True).distinct()
        )
        serialized.append(
            {
                "id": str(chain.id),
                "title": chain.title,
                "summary": chain.summary,
                "projects": [p for p in projects if p],
                "assistants": [a for a in assistants if a],
            }
        )
    return Response(serialized)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def link_chain_to_thread(request):
    warnings.warn(
        "Deprecated: use /api/v1/memory/chains/link_thread/",
        DeprecationWarning,
    )
    chain_id = request.data.get("chain_id")
    thread_id = request.data.get("thread_id")
    if not chain_id or not thread_id:
        return Response({"error": "chain_id and thread_id required"}, status=400)

    chain = get_object_or_404(MemoryChain, id=chain_id)
    thread = get_object_or_404(NarrativeThread, id=thread_id)
    chain.thread = thread
    chain.save(update_fields=["thread"])
    return Response(MemoryChainSerializer(chain).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def cross_project_recall_view(request, chain_id):
    chain = get_object_or_404(MemoryChain, id=chain_id)
    memories = recall_from_thread(chain)
    serializer = MemoryEntrySerializer(memories, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def reflect_on_memory(request):
    memory_ids = request.data.get("memory_ids", [])
    if not memory_ids:
        return Response({"error": "No memory IDs provided."}, status=400)
    try:
        reflection = service_reflect_on_memory(memory_ids)
    except ValueError as exc:
        return Response({"error": str(exc)}, status=400)

    memories = MemoryEntry.objects.filter(id__in=memory_ids)
    if not memories.exists():
        return Response({"error": "No valid memories found."}, status=400)

    combined_text = "\n\n".join([m.event for m in memories])

    prompt = f"""
    Summarize the following experiences into a coherent reflection that captures lessons learned, emotional tone, and overall patterns:

    {combined_text}
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are an expert in emotional intelligence and personal growth.",
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.7,
        max_tokens=1024,
    )

    summary = response.choices[0].message.content.strip()

    reflection = get_memory_service().log_reflection(summary, memories)

    return Response({"summary": summary, "reflection_id": reflection.id})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def reflect_on_memories(request):
    """
    Generate a reflection across multiple memories.
    """
    memory_ids = request.data.get("memory_ids", [])
    if not memory_ids:
        return Response({"error": "No memory IDs provided"}, status=400)

    memories = MemoryEntry.objects.filter(id__in=memory_ids).order_by("timestamp")
    if not memories.exists():
        return Response({"error": "No memories found"}, status=404)

    combined_text = "\n\n".join([f"- {m.event}" for m in memories])

    # 🧠 Now send to GPT
    from openai import OpenAI

    client = OpenAI()

    prompt = (
        "Summarize the following memories into an insightful, thoughtful reflection. "
        "Capture emotional patterns, major events, and potential lessons:\n\n"
        f"{combined_text}"
    )

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
        max_tokens=1024,
    )

    reflection_text = response.choices[0].message.content.strip()

    reflection = get_memory_service().log_reflection(
        reflection_text,
        memories,
    )

    return Response({"reflection": reflection.summary})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def save_reflection(request):
    """
    Save a new ReflectionLog from a title, summary, and selected memories.
    """
    title = request.data.get("title")
    summary = request.data.get("summary")
    memory_ids = request.data.get("memory_ids", [])

    if not (title and summary and memory_ids):
        return Response({"error": "Missing required fields"}, status=400)

    memories = MemoryEntry.objects.filter(id__in=memory_ids)
    reflection = get_memory_service().log_reflection(summary, memories)

    reflection.title = title
    reflection.save(update_fields=["title"])

    return Response({"message": "Reflection saved successfully!"})


@api_view(["GET", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def memory_detail(request, id):
    memory = get_object_or_404(MemoryEntry, id=id)

    if request.method == "GET":
        serializer = MemoryEntrySerializer(memory)
        return Response(serializer.data)

    elif request.method == "PATCH":
        memory.event = request.data.get("event", memory.event)
        memory.emotion = request.data.get("emotion", memory.emotion)
        memory.importance = request.data.get("importance", memory.importance)
        memory.related_project = request.data.get(
            "related_project", memory.related_project
        )
        memory.save()
        serializer = MemoryEntrySerializer(memory)
        return Response(serializer.data)

    elif request.method == "DELETE":
        memory.delete()
        return Response(status=204)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def bookmark_memory(request, memory_id):
    warnings.warn(
        "Deprecated: use /api/v1/memory/entries/<id>/bookmark/",
        DeprecationWarning,
    )
    memory = get_object_or_404(MemoryEntry, id=memory_id)
    label = request.data.get("label")
    memory.is_bookmarked = True
    memory.bookmark_label = label
    memory.save()
    return Response(MemoryEntrySerializer(memory).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def unbookmark_memory(request, memory_id):
    warnings.warn(
        "Deprecated: use /api/v1/memory/entries/<id>/unbookmark/",
        DeprecationWarning,
    )
    memory = get_object_or_404(MemoryEntry, id=memory_id)
    memory.is_bookmarked = False
    memory.bookmark_label = None
    memory.save()
    return Response(MemoryEntrySerializer(memory).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def bookmarked_memories(request):
    queryset = MemoryEntry.objects.filter(is_bookmarked=True).order_by("-created_at")
    assistant_slug = request.GET.get("assistant")
    project_id = request.GET.get("project")
    label = request.GET.get("label")
    tag_slug = request.GET.get("tag")
    date = request.GET.get("date")

    if assistant_slug:
        queryset = queryset.filter(assistant__slug=assistant_slug)
    if project_id:
        queryset = queryset.filter(related_project_id=project_id)
    if label:
        queryset = queryset.filter(bookmark_label__icontains=label)
    if tag_slug:
        queryset = queryset.filter(tags__slug=tag_slug)
    if date:
        queryset = queryset.filter(created_at__date=date)

    return Response(MemoryEntrySerializer(queryset, many=True).data)


@api_view(["POST"])
def save_memory(request):
    data = request.data
    event = data.get("event")

    if not event:
        return Response(
            {"error": "Memory event is required."}, status=status.HTTP_400_BAD_REQUEST
        )

    memory = MemoryEntry.objects.create(
        event=event,
        emotion=data.get("emotion"),
        importance=data.get("importance", 5),
        related_project=data.get("related_project"),
        triggered_by=f"manual: {event[:40]}",
    )

    # ✅ Save embedding for this memory
    save_embedding(memory, embedding=[])

    return Response({"message": "Memory saved", "memory_id": memory.id})


@api_view(["GET"])
def recent_memories(request):
    """
    Fetch the 10 most recent memories.
    """
    memories = MemoryEntry.objects.all().order_by("-timestamp")[:10]
    serializer = MemoryEntrySerializer(memories, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def list_memories(request):
    if _rate_limited(request, "list_memories"):
        resp = Response({"detail": "rate limit"}, status=429)
        resp["X-Rate-Limited"] = "true"
        return resp
    queryset = MemoryEntry.objects.all().order_by("-created_at")

    # Optional filters
    assistant_slug = request.GET.get("assistant_slug")
    assistant_id = request.GET.get("assistant_id")
    is_conversation = request.GET.get("is_conversation")
    project_id = request.GET.get("project_id")
    emotion = request.GET.get("emotion")
    symbolic_change = request.GET.get("symbolic_change")
    campaign_id = request.GET.get("campaign_id")

    if assistant_slug:
        queryset = queryset.filter(linked_thought__assistant__slug=assistant_slug)
    if assistant_id:
        try:
            uuid_val = uuid.UUID(str(assistant_id))
            queryset = queryset.filter(assistant_id=uuid_val)
        except (ValueError, TypeError):
            queryset = queryset.filter(linked_thought__assistant__slug=assistant_id)

    if is_conversation in ["true", "1", "yes"]:
        queryset = queryset.filter(is_conversation=True)

    if project_id:
        queryset = queryset.filter(related_project_id=project_id)

    if emotion:
        queryset = queryset.filter(emotion=emotion)

    if symbolic_change in ["true", "1", "yes"]:
        queryset = queryset.filter(symbolic_change=True)

    if campaign_id:
        queryset = queryset.filter(related_campaign_id=campaign_id)

    serializer = MemoryEntrySerializer(queryset, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def upload_voice_clip(request):
    memory_id = request.data.get("memory_id")
    voice_clip = request.FILES.get("voice_clip")

    if not memory_id or not voice_clip:
        return Response(
            {"error": "Missing memory_id or voice_clip"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        memory = MemoryEntry.objects.get(id=memory_id)
        memory.voice_clip = voice_clip
        memory.save()
        return Response({"message": "Voice clip uploaded successfully."})
    except MemoryEntry.DoesNotExist:
        return Response(
            {"error": "Memory not found."}, status=status.HTTP_404_NOT_FOUND
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def submit_memory_feedback(request):
    serializer = MemoryFeedbackSerializer(data=request.data)
    if serializer.is_valid():
        feedback = serializer.save(
            submitted_by=request.user if request.user.is_authenticated else None
        )

        from .feedback_engine import check_auto_suppress

        check_auto_suppress(feedback.memory)
        return Response(serializer.data, status=201)

    return Response(serializer.errors, status=400)


@api_view(["GET"])
def list_memory_feedback(request, memory_id):
    feedback_qs = MemoryFeedback.objects.filter(memory_id=memory_id)
    status_param = request.query_params.get("status")
    if status_param:
        feedback_qs = feedback_qs.filter(status=status_param)
    feedback = feedback_qs.order_by("-created_at")
    serializer = MemoryFeedbackSerializer(feedback, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mutate_memory(request, id):
    warnings.warn(
        "Deprecated: use /api/v1/memory/entries/<id>/mutate/",
        DeprecationWarning,
    )
    """Mutate a memory entry using the specified style."""
    try:
        memory = MemoryEntry.objects.get(id=id)
    except MemoryEntry.DoesNotExist:
        return Response({"error": "Memory not found"}, status=404)

    style = request.data.get("style", "clarify")
    base_text = memory.summary or memory.event or memory.full_transcript or ""
    mutated = run_mutation(base_text, style)

    new_kwargs = {
        "assistant": memory.assistant,
        "related_project": memory.related_project,
        "type": "mutation",
        "parent_memory": memory,
        "triggered_by": "memory mutation",
    }
    if memory.summary:
        new_kwargs["event"] = memory.event
        new_kwargs["summary"] = mutated
    else:
        new_kwargs["event"] = mutated

    new_mem = MemoryEntry.objects.create(**new_kwargs)
    if memory.tags.exists():
        new_mem.tags.set(memory.tags.all())

    try:
        vector = get_embedding_for_text(mutated)
        if vector:
            save_embedding(new_mem, vector)
            get_memory_service().auto_tag_memory_from_text(new_mem, mutated)
    except Exception:
        pass

    if memory.assistant:
        get_memory_service().log_assistant_meta(
            memory.assistant,
            f"Refined memory {memory.id} using style '{style}' based on feedback.",
            linked_memory=new_mem,
        )

    serializer = MemoryEntrySerializer(new_mem)
    return Response(serializer.data, status=201)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def train_prompts_from_memories(request):
    memory_ids = request.data.get("memory_ids", [])
    if not memory_ids:
        return Response({"error": "No memories selected."}, status=400)

    memories = MemoryEntry.objects.filter(id__in=memory_ids)

    memory_texts = "\n".join(
        [
            f"- {m.event} (Emotion: {m.emotion or 'Neutral'}, Importance: {m.importance}/10)"
            for m in memories
        ]
    )

    instruction = f"""
You are a prompt engineer creating a new SYSTEM prompt based on important personal memories.
Write a concise, powerful SYSTEM prompt that guides an assistant to behave in alignment with the following life events:

{memory_texts}

The prompt should focus on emotions, lessons learned, and goals. Make it inspirational but practical.
"""

    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": instruction}],
        temperature=0.4,
        max_tokens=1024,
    )

    generated_prompt = response.choices[0].message.content.strip()

    # Save it as a Prompt
    new_prompt = Prompt.objects.create(
        title=f"System Prompt from Memories {timezone.now().strftime('%Y-%m-%d')}",
        type="system",
        content=generated_prompt,
        source="memory-trainer",
        token_count=len(generated_prompt.split()),
    )
    save_embedding(new_prompt, embedding=[])
    serializer = PromptSerializer(new_prompt)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_memory_with_tags(request):
    """
    Create a memory entry and assign tags by name.
    Example POST body:
    {
        "event": "Met with Brooklyn to discuss vision boards.",
        "emotion": "inspired",
        "importance": 8,
        "related_project": null,
        "tags": ["planning", "emotional-growth"]
    }
    """
    from mcp_core.models import Tag
    from memory.utils.tag_utils import normalize_tag_name

    data = request.data
    tag_names = data.pop("tags", [])

    if "event" not in data:
        return Response({"error": "Missing required field: event"}, status=400)

    memory = MemoryEntry.objects.create(
        event=data["event"],
        emotion=data.get("emotion"),
        importance=data.get("importance", 5),
        related_project=data.get("related_project"),
        triggered_by="api:create",
    )

    tag_objs = []
    for name in tag_names:
        norm_name, slug = normalize_tag_name(name)
        tag, _ = Tag.objects.get_or_create(slug=slug, defaults={"name": norm_name})
        tag_objs.append(tag)

    memory.tags.set(tag_objs)
    save_embedding(memory, embedding=[])

    serializer = MemoryEntrySerializer(memory)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def memories_by_tag(request, slug):
    from mcp_core.models import Tag

    try:
        tag = Tag.objects.get(slug=slug)
    except Tag.DoesNotExist:
        return Response({"error": f"Tag '{slug}' not found."}, status=404)

    memories = MemoryEntry.objects.filter(tags=tag).order_by("-created_at")
    serializer = MemoryEntrySerializer(memories, many=True)
    return Response(serializer.data)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_memory_tags(request, id):
    from mcp_core.models import Tag
    from memory.utils.tag_utils import normalize_tag_name

    memory = get_object_or_404(MemoryEntry, id=id)
    tag_names = request.data.get("tags", [])

    if not isinstance(tag_names, list):
        return Response({"error": "tags must be a list of strings"}, status=400)

    tag_objs = []
    for name in tag_names:
        norm_name, slug = normalize_tag_name(name)
        tag, _ = Tag.objects.get_or_create(slug=slug, defaults={"name": norm_name})
        tag_objs.append(tag)

    memory.tags.set(tag_objs)
    memory.save()

    serializer = MemoryEntrySerializer(memory)
    return Response(serializer.data)


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def replace_memory(request, id):
    from mcp_core.models import Tag
    from memory.utils.tag_utils import normalize_tag_name

    memory = get_object_or_404(MemoryEntry, id=id)
    data = request.data

    memory.event = data.get("event", memory.event)
    memory.emotion = data.get("emotion", memory.emotion)
    memory.importance = data.get("importance", memory.importance)
    memory.related_project = data.get("related_project", memory.related_project)
    memory.save()

    tag_names = data.get("tags", [])
    if isinstance(tag_names, list):
        tag_objs = []
        for name in tag_names:
            norm_name, slug = normalize_tag_name(name)
            tag, _ = Tag.objects.get_or_create(slug=slug, defaults={"name": norm_name})
            tag_objs.append(tag)
        memory.tags.set(tag_objs)

    serializer = MemoryEntrySerializer(memory)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def assistant_memories(request, slug):
    assistant, memories = get_memory_service().get_assistant_memories(slug)
    if assistant is None:
        return Response({"error": "Assistant not found"}, status=404)

    serializer = MemoryEntrySerializer(memories, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def vector_memories(request):
    entries = MemoryEntry.objects.filter(type="vector_search").order_by("-created_at")[
        :25
    ]
    serializer = MemoryEntrySerializer(entries, many=True)
    return Response(serializer.data)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def shared_memory_pools(request):
    """Create or list shared memory pools."""
    if request.method == "POST":
        serializer = SharedMemoryPoolSerializer(data=request.data)
        if serializer.is_valid():
            pool = serializer.save()
            return Response(SharedMemoryPoolSerializer(pool).data, status=201)
        return Response(serializer.errors, status=400)

    pools = SharedMemoryPool.objects.all().order_by("-created_at")
    serializer = SharedMemoryPoolSerializer(pools, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def shared_memory_pool_detail(request, pool_id):
    pool = get_object_or_404(SharedMemoryPool, id=pool_id)
    serializer = SharedMemoryPoolSerializer(pool)
    return Response(serializer.data)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def shared_memory_pool_entries(request, pool_id):
    pool = get_object_or_404(SharedMemoryPool, id=pool_id)
    if request.method == "POST":
        data = request.data.copy()
        data["pool"] = str(pool.id)
        serializer = SharedMemoryEntrySerializer(data=data)
        if serializer.is_valid():
            entry = serializer.save(pool=pool)
            return Response(SharedMemoryEntrySerializer(entry).data, status=201)
        return Response(serializer.errors, status=400)

    entries = pool.entries.order_by("-created_at")
    serializer = SharedMemoryEntrySerializer(entries, many=True)
    return Response(serializer.data)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def memory_braids(request):
    """List or create BraidedMemoryStrand objects."""
    if request.method == "POST":
        serializer = BraidedMemoryStrandSerializer(data=request.data)
        if serializer.is_valid():
            strand = serializer.save()
            return Response(BraidedMemoryStrandSerializer(strand).data, status=201)
        return Response(serializer.errors, status=400)

    strands = BraidedMemoryStrand.objects.all().order_by("-created_at")
    serializer = BraidedMemoryStrandSerializer(strands, many=True)
    return Response(serializer.data)


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def continuity_anchors(request):
    """List or create ContinuityAnchorPoint objects."""
    if request.method == "POST":
        serializer = ContinuityAnchorPointSerializer(data=request.data)
        if serializer.is_valid():
            anchor = serializer.save()
            return Response(ContinuityAnchorPointSerializer(anchor).data, status=201)
        return Response(serializer.errors, status=400)

    anchors = ContinuityAnchorPoint.objects.all().order_by("-created_at")
    serializer = ContinuityAnchorPointSerializer(anchors, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def symbolic_anchors(request):
    """List SymbolicMemoryAnchor objects with optional search and sorting."""
    anchors = SymbolicMemoryAnchor.objects.all()
    assistant = request.GET.get("assistant")
    show_empty = request.GET.get("show_empty") == "true"
    query = request.GET.get("q")
    order_by = request.GET.get("order_by")
    mutation_status = request.GET.get("mutation_status")

    if assistant:
        try:
            uuid.UUID(str(assistant))
            anchors = anchors.filter(reinforced_by__id=assistant)
        except ValueError:
            anchors = anchors.filter(reinforced_by__slug=assistant)

    if query:
        anchors = anchors.filter(label__icontains=query)

    if mutation_status:
        anchors = anchors.filter(mutation_status=mutation_status)

    anchors = anchors.order_by(order_by or "slug")
    serializer = SymbolicMemoryAnchorSerializer(anchors, many=True)
    data = serializer.data

    if not show_empty:
        data = [
            a
            for a in data
            if (a.get("chunks_count") or 0) > 0 or (a.get("retagged_count") or 0) > 0
        ]

    drift_gt = request.GET.get("drift_gt")
    avg_score_gt = request.GET.get("avg_score_gt")

    if drift_gt:
        data = [a for a in data if (a.get("drift_score") or 0) >= float(drift_gt)]

    if avg_score_gt:
        data = [a for a in data if (a.get("avg_score") or 0) >= float(avg_score_gt)]

    return Response({"results": data})


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_symbolic_anchor(request, pk):
    """Update a SymbolicMemoryAnchor."""
    anchor = get_object_or_404(SymbolicMemoryAnchor, id=pk)
    serializer = SymbolicMemoryAnchorSerializer(anchor, data=request.data, partial=True)
    if serializer.is_valid():
        orig_label = anchor.label
        anchor = serializer.save()
        if (
            "label" in serializer.validated_data
            and serializer.validated_data["label"] != orig_label
        ):
            anchor.mutated_from = orig_label
            anchor.mutated_reason = "manual_edit"
            anchor.save(update_fields=["mutated_from", "mutated_reason"])
        return Response(SymbolicMemoryAnchorSerializer(anchor).data)
    return Response(serializer.errors, status=400)


@api_view(["PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def glossary_anchor_detail(request, slug):
    """Rename or delete a SymbolicMemoryAnchor identified by slug."""
    anchor = get_object_or_404(SymbolicMemoryAnchor, slug=slug)

    if request.method == "DELETE":
        anchor.delete()
        return Response(status=204)

    serializer = SymbolicMemoryAnchorSerializer(anchor, data=request.data, partial=True)
    if serializer.is_valid():
        old_slug = anchor.slug
        orig_label = anchor.label
        anchor = serializer.save()
        if (
            "label" in serializer.validated_data
            and serializer.validated_data["label"] != orig_label
        ):
            anchor.mutated_from = orig_label
            anchor.mutated_reason = "manual_edit"
            anchor.save(update_fields=["mutated_from", "mutated_reason"])
        if old_slug != anchor.slug and request.GET.get("auto_retag") == "true":
            from intel_core.models import DocumentChunk

            chunks = DocumentChunk.objects.filter(matched_anchors__contains=[old_slug])
            for chunk in chunks:
                changed = False
                anchors = list(chunk.matched_anchors)
                while old_slug in anchors:
                    anchors.remove(old_slug)
                    changed = True
                if anchor.slug not in anchors:
                    anchors.append(anchor.slug)
                    changed = True
                if chunk.anchor_id and chunk.anchor_id == anchor.id:
                    chunk.anchor = anchor
                    changed = True
                if changed:
                    chunk.matched_anchors = anchors
                    chunk.save(update_fields=["matched_anchors", "anchor"])
        return Response(SymbolicMemoryAnchorSerializer(anchor).data)
    return Response(serializer.errors, status=400)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def boost_anchor(request):
    """Set glossary_boost on all chunks for a given anchor slug."""
    slug = request.data.get("anchor")
    boost = float(request.data.get("boost", 0))
    if not slug:
        return Response({"error": "anchor required"}, status=400)
    anchor = get_object_or_404(SymbolicMemoryAnchor, slug=slug)
    from intel_core.models import DocumentChunk

    updated = DocumentChunk.objects.filter(anchor=anchor).update(glossary_boost=boost)
    return Response({"updated": updated, "boost": boost})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def anamnesis(request):
    """Recover fragmented memory for an assistant."""
    slug = request.data.get("assistant_slug")
    if not slug:
        return Response({"error": "assistant_slug required"}, status=400)
    assistant = get_object_or_404(Assistant, slug=slug)
    data = run_anamnesis_retrieval(assistant)
    return Response(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def public_memory_grove(request):
    """Query public memory groves by codex or tags."""

    codex = request.GET.get("codex")
    if codex:
        queryset = queryset.filter(codex_reference__id=codex)

    memory_tag = request.GET.get("memory_tag")
    if memory_tag:
        queryset = queryset.filter(featured_memories__tags__slug=memory_tag)

    assistant = request.GET.get("assistant")
    if assistant:
        queryset = queryset.filter(featured_memories__linked_agents__id=assistant)

    queryset = queryset.distinct()

    data = [
        {
            "grove_name": g.grove_name,
            "linked_cluster": g.linked_cluster_id,
            "codex_reference": g.codex_reference_id,
            "memory_count": g.featured_memories.count(),
        }
        for g in queryset
    ]
    return Response(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def symbolic_chunk_diff_view(request, document_set_id):
    """Return failed chunks for a document set for comparison."""
    failures = MemoryEmbeddingFailureLog.objects.filter(document_set_id=document_set_id)
    diff = [
        {
            "chunk_index": f.chunk_index,
            "text": f.text,
            "error_message": f.error_message,
            "resolved": f.resolved,
        }
        for f in failures
    ]
    return Response({"document_set_id": str(document_set_id), "chunks": diff})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def suggest_memory_merge(request):
    """Create a merge suggestion for two memory entries."""
    serializer = MemoryMergeSuggestionSerializer(data=request.data)
    if serializer.is_valid():
        suggestion = serializer.save()
        return Response(
            MemoryMergeSuggestionSerializer(suggestion).data,
            status=status.HTTP_201_CREATED,
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def glossary_retry_logs(request):
    """Return recent GlossaryRetryLog entries."""
    logs = GlossaryRetryLog.objects.all().order_by("-created_at")[:20]
    data = GlossaryRetryLogSerializer(logs, many=True).data
    return Response({"results": data})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def keeper_log_list(request):
    """List GlossaryKeeperLog entries."""
    qs = GlossaryKeeperLog.objects.select_related("anchor", "assistant")
    assistant_slug = request.GET.get("assistant")
    if assistant_slug:
        qs = qs.filter(assistant__slug=assistant_slug)
    action = request.GET.get("action")
    if action:
        qs = qs.filter(action_taken=action)
    logs = qs.order_by("-timestamp")
    paginator = PageNumberPagination()
    page = paginator.paginate_queryset(logs, request)
    serializer = GlossaryKeeperLogSerializer(page, many=True)
    return paginator.get_paginated_response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def glossary_overlay(request):
    """Return anchors configured for tooltip display."""
    location = request.query_params.get("location")
    anchors = SymbolicMemoryAnchor.objects.filter(display_tooltip=True)
    if location:
        anchors = anchors.filter(display_location__contains=[location])
    data = [
        {
            "label": a.label,
            "definition": a.description,
            "tooltip": a.glossary_guidance,
            "slug": a.slug,
            "anchor_id": str(a.id),
            "location": location,
        }
        for a in anchors
    ]
    return Response({"results": data})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def anchor_convergence_logs(request, slug):
    """Return recent AnchorConvergenceLog entries for an anchor."""
    anchor = get_object_or_404(SymbolicMemoryAnchor, slug=slug)

    qs = anchor.convergence_logs.select_related("assistant", "memory")
    assistant_id = request.GET.get("assistant")
    if assistant_id:
        qs = qs.filter(assistant_id=assistant_id)

    logs = qs.order_by("-created_at")[:20]
    data = AnchorConvergenceLogSerializer(logs, many=True).data
    return Response({"results": data})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def assistant_convergence_logs(request):
    """Return recent AnchorConvergenceLog entries for an assistant."""
    assistant_id = request.GET.get("assistant")
    if not assistant_id:
        return Response({"results": []})

    qs = AnchorConvergenceLog.objects.select_related(
        "assistant", "memory", "anchor"
    ).filter(assistant_id=assistant_id)
    logs = qs.order_by("-created_at")[:20]
    data = AnchorConvergenceLogSerializer(logs, many=True).data
    return Response({"results": data})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def anchor_training(request, slug):
    """Return training memories and chunks for an anchor."""
    anchor = get_object_or_404(SymbolicMemoryAnchor, slug=slug)
    memories = anchor.memories.all().order_by("-created_at")[:20]
    from intel_core.models import DocumentChunk, GlossaryFallbackReflectionLog
    from intel_core.serializers import DocumentChunkInfoSerializer

    chunks = DocumentChunk.objects.filter(anchor=anchor).order_by("-created_at")[:20]
    fallbacks = GlossaryFallbackReflectionLog.objects.filter(anchor_slug=slug).order_by(
        "-created_at"
    )[:20]
    reinforcements = AnchorReinforcementLog.objects.filter(anchor=anchor).order_by(
        "-created_at"
    )[:20]

    data = {
        "memories": MemoryEntrySlimSerializer(memories, many=True).data,
        "chunks": DocumentChunkInfoSerializer(chunks, many=True).data,
        "fallbacks": [
            {
                "id": str(f.id),
                "chunk_id": f.chunk_id,
                "match_score": f.match_score,
                "created_at": f.created_at,
            }
            for f in fallbacks
        ],
        "reinforcements": AnchorReinforcementLogSerializer(
            reinforcements, many=True
        ).data,
    }
    return Response(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def glossary_mutations(request):
    """Return SymbolicMemoryAnchor records with pending mutations."""
    anchors = SymbolicMemoryAnchor.objects.exclude(
        mutation_source__isnull=True
    ).exclude(mutation_source="")
    include_all = request.query_params.get("include") == "all"
    if not include_all:
        anchors = anchors.filter(mutation_status="pending")
    assistant_slug = request.query_params.get("assistant")
    if assistant_slug:
        anchors = anchors.filter(assistant__slug=assistant_slug)
    data = []
    for a in anchors:
        from memory.services.convergence import calculate_convergence_stats

        stats = calculate_convergence_stats(a)
        data.append(
            {
                "id": str(a.id),
                "original_label": a.label,
                "suggested_label": a.suggested_label,
                "mutation_source": a.mutation_source,
                "fallback_count": stats.get("fallback_count"),
                "mutation_score": stats.get("mutation_score"),
                "status": a.mutation_status,
            }
        )
    return Response({"results": data})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def accept_glossary_mutation(request, id):
    """Apply the suggested label and mark mutation as applied."""
    anchor = get_object_or_404(SymbolicMemoryAnchor, id=id)
    if not anchor.suggested_label:
        return Response({"error": "no suggestion"}, status=400)
    old_label = anchor.label
    anchor.label = anchor.suggested_label
    anchor.suggested_label = None
    anchor.mutation_status = "applied"
    anchor.mutated_from = old_label
    anchor.mutated_reason = "auto_generated"
    anchor.save(
        update_fields=[
            "label",
            "suggested_label",
            "mutation_status",
            "mutated_from",
            "mutated_reason",
        ]
    )
    if anchor.assistant_id:
        from memory.services.mutation_memory import generate_mutation_memory_entry

        mem = generate_mutation_memory_entry(
            anchor, anchor.assistant, original_label=old_label
        )
        if mem:
            anchor.explanation = f"mutation_memory:{mem.id}"
            anchor.save(update_fields=["explanation"])
    try:
        reinforce_glossary_anchor(
            anchor,
            assistant=anchor.assistant,
            source="mutation_applied",
            score=1.0,
        )
        update_anchor_acquisition(anchor, "reinforced")
        from memory.services.convergence import recalculate_anchor_convergence

        recalculate_anchor_convergence(anchor)
    except Exception:
        pass
    return Response({"status": "applied"})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def reject_glossary_mutation(request, id):
    """Mark a glossary mutation as rejected."""
    anchor = get_object_or_404(SymbolicMemoryAnchor, id=id)
    anchor.mutation_status = "rejected"
    anchor.mutated_reason = "rejected"
    anchor.save(update_fields=["mutation_status", "mutated_reason"])
    try:
        from memory.services.convergence import recalculate_anchor_convergence

        recalculate_anchor_convergence(anchor)
    except Exception:
        pass
    return Response({"status": "rejected"})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def accept_mutation(request, id):
    """Mark a glossary mutation as accepted without applying the label."""
    anchor = get_object_or_404(SymbolicMemoryAnchor, id=id)
    if getattr(anchor, "status", None) == "pending":
        anchor.status = "accepted"
        anchor.save(update_fields=["status"])
    return Response({"status": anchor.status})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def accept_replay(request, id):
    replay = get_object_or_404(ReflectionReplayLog, id=id)
    if replay.original_reflection and replay.replayed_summary:
        replay.original_reflection.summary = replay.replayed_summary
        replay.original_reflection.save(update_fields=["summary"])
    replay.status = ReflectionReplayLog.ReplayStatus.ACCEPTED
    replay.save(update_fields=["status"])
    return Response({"status": "accepted"})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def reject_replay(request, id):
    replay = get_object_or_404(ReflectionReplayLog, id=id)
    replay.status = ReflectionReplayLog.ReplayStatus.SKIPPED
    replay.save(update_fields=["status"])
    return Response({"status": "skipped"})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def anchor_diagnostics(request):
    """Return basic diagnostics for all anchors."""
    from django.db.models import Avg, Count
    from intel_core.models import ChunkTag

    anchors = SymbolicMemoryAnchor.objects.all()
    data = []
    for a in anchors:
        chunk_count = a.chunks.count()
        linked_count = ChunkTag.objects.filter(name=a.slug).count()
        fallback_count = GlossaryFallbackReflectionLog.objects.filter(
            anchor_slug=a.slug
        ).count()
        qs = RAGGroundingLog.objects.filter(expected_anchor=a.slug)
        avg_score = qs.aggregate(avg=Avg("adjusted_score")).get("avg") or 0.0
        match_rate = 0.0
        if qs.exists():
            match_rate = qs.filter(fallback_triggered=False).count() / qs.count()
        data.append(
            {
                "slug": a.slug,
                "label": a.label,
                "chunk_count": chunk_count,
                "fallback_count": fallback_count,
                "linked_chunks_count": linked_count,
                "avg_score": round(avg_score, 2),
                "match_rate": round(match_rate, 2),
                "auto_suppressed": a.auto_suppressed,
                "assistant": a.assistant.slug if a.assistant else None,
            }
        )
    duplicates = (
        SymbolicMemoryAnchor.objects.values("slug")
        .annotate(count=Count("id"))
        .filter(count__gt=1)
    )
    return Response({"results": data, "duplicates": list(duplicates)})


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def anchor_suggestions(request):
    """List AnchorSuggestion objects with optional filters."""
    qs = AnchorSuggestion.objects.all()
    assistant = request.GET.get("assistant")
    status = request.GET.get("status")
    term = request.GET.get("term")
    if assistant:
        qs = qs.filter(assistant__slug=assistant)
    if status:
        qs = qs.filter(status=status)
    if term:
        qs = qs.filter(term__icontains=term)
    qs = qs.order_by("-created_at")
    serializer = AnchorSuggestionSerializer(qs, many=True)
    return Response({"results": serializer.data})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def accept_anchor_suggestion(request, id):
    """Accept an anchor suggestion and create the anchor if needed."""
    suggestion = get_object_or_404(AnchorSuggestion, id=id)
    if suggestion.status != "accepted":
        anchor = suggestion.original_anchor
        if not anchor:
            anchor, _ = SymbolicMemoryAnchor.objects.get_or_create(
                slug=suggestion.slug,
                defaults={
                    "label": suggestion.term.title(),
                    "source": "rag_suggest",
                    "created_from": "rag_suggest",
                    "assistant": suggestion.assistant,
                },
            )
            suggestion.original_anchor = anchor
        suggestion.status = "accepted"
        suggestion.save(update_fields=["status", "original_anchor"])
        try:
            from memory.services.reinforcement import reinforce_glossary_anchor

            reinforce_glossary_anchor(
                anchor,
                assistant=suggestion.assistant,
                source="suggestion_accept",
                outcome="boosted",
                score=1.0,
                score_delta=1.0,
            )
        except Exception:
            pass
    return Response(AnchorSuggestionSerializer(suggestion).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def reject_anchor_suggestion(request, id):
    suggestion = get_object_or_404(AnchorSuggestion, id=id)
    suggestion.status = "rejected"
    suggestion.save(update_fields=["status"])
    return Response({"status": "rejected"})


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def edit_anchor_suggestion(request, id):
    suggestion = get_object_or_404(AnchorSuggestion, id=id)
    slug = request.data.get("slug")
    term = request.data.get("term")
    changed = False
    if slug:
        suggestion.slug = slug
        changed = True
    if term:
        suggestion.term = term
        changed = True
    if changed:
        suggestion.save(update_fields=["slug", "term"])
    return Response(AnchorSuggestionSerializer(suggestion).data)
