from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from django.db.models import Q
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import (
    MemoryEntry,
    MemoryChain,
    MemoryFeedback,
    SharedMemoryPool,
    SharedMemoryEntry,
)
from .serializers import (
    MemoryEntrySerializer,
    MemoryFeedbackSerializer,
    MemoryChainSerializer,
    SharedMemoryPoolSerializer,
    SharedMemoryEntrySerializer,
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
from mcp_core.utils.auto_tag_from_embedding import auto_tag_from_embedding
from assistants.helpers.logging_helper import log_assistant_thought
from assistants.models import Assistant, AssistantThoughtLog, AssistantReflectionLog
from mcp_core.models import NarrativeThread
from memory.utils.thread_helpers import get_linked_chains, recall_from_thread

load_dotenv()

client = OpenAI()


@api_view(["POST"])
@permission_classes([AllowAny])
def create_memory_chain(request):
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
@permission_classes([AllowAny])
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
@permission_classes([AllowAny])
def list_memory_chains(request):
    chains = MemoryChain.objects.all().order_by("-created_at")
    data = [
        {"id": str(chain.id), "title": chain.title, "created_at": chain.created_at}
        for chain in chains
    ]
    return Response(data)


@api_view(["GET"])
@permission_classes([AllowAny])
def summarize_chain_view(request, chain_id):
    chain = get_object_or_404(MemoryChain, id=chain_id)
    from .utils.chain_helpers import summarize_memory_chain

    summary = summarize_memory_chain(chain)
    return Response({"chain_id": str(chain.id), "summary": summary})


@api_view(["GET"])
@permission_classes([AllowAny])
def chain_flowmap_view(request, chain_id):
    chain = get_object_or_404(MemoryChain, id=chain_id)
    from .utils.chain_helpers import generate_flowmap_from_chain

    data = generate_flowmap_from_chain(chain)
    return Response(data)


@api_view(["GET"])
@permission_classes([AllowAny])
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
@permission_classes([AllowAny])
def link_chain_to_thread(request):
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
@permission_classes([AllowAny])
def cross_project_recall_view(request, chain_id):
    chain = get_object_or_404(MemoryChain, id=chain_id)
    memories = recall_from_thread(chain)
    serializer = MemoryEntrySerializer(memories, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([AllowAny])
def reflect_on_memory(request):
    memory_ids = request.data.get("memory_ids", [])
    if not memory_ids:
        return Response({"error": "No memory IDs provided."}, status=400)
    try:
        reflection = service_reflect_on_memory(memory_ids)
    except ValueError as exc:
        return Response({"error": str(exc)}, status=400)

    return Response({"summary": reflection.summary, "reflection_id": reflection.id})


@api_view(["POST"])
@permission_classes([AllowAny])
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

    # Save reflection
    reflection = AssistantReflectionLog.objects.create(
        summary=reflection_text,
        time_period_start=memories.first().timestamp,
        time_period_end=memories.last().timestamp,
    )
    reflection.linked_memories.set(memories)
    save_embedding(reflection, embedding=[])

    return Response({"reflection": reflection.summary})


@api_view(["POST"])
@permission_classes([AllowAny])
def save_reflection(request):
    """
    Save a new ReflectionLog from a title, summary, and selected memories.
    """
    title = request.data.get("title")
    summary = request.data.get("summary")
    memory_ids = request.data.get("memory_ids", [])

    if not (title and summary and memory_ids):
        return Response({"error": "Missing required fields"}, status=400)

    reflection = AssistantReflectionLog.objects.create(
        summary=summary,
        time_period_start=timezone.now(),  # You can make smarter if needed
        time_period_end=timezone.now(),
    )
    reflection.linked_memories.set(MemoryEntry.objects.filter(id__in=memory_ids))
    reflection.save()
    save_embedding(reflection, embedding=[])

    return Response({"message": "Reflection saved successfully!"})


@api_view(["GET", "PATCH", "DELETE"])
@permission_classes([AllowAny])
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
@permission_classes([AllowAny])
def bookmark_memory(request, memory_id):
    memory = get_object_or_404(MemoryEntry, id=memory_id)
    label = request.data.get("label")
    memory.is_bookmarked = True
    memory.bookmark_label = label
    memory.save()
    return Response(MemoryEntrySerializer(memory).data)


@api_view(["POST"])
@permission_classes([AllowAny])
def unbookmark_memory(request, memory_id):
    memory = get_object_or_404(MemoryEntry, id=memory_id)
    memory.is_bookmarked = False
    memory.bookmark_label = None
    memory.save()
    return Response(MemoryEntrySerializer(memory).data)


@api_view(["GET"])
@permission_classes([AllowAny])
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
@permission_classes([AllowAny])
def list_memories(request):
    queryset = MemoryEntry.objects.all().order_by("-created_at")

    # Optional filters
    assistant_slug = request.GET.get("assistant_slug")
    is_conversation = request.GET.get("is_conversation")
    project_id = request.GET.get("project_id")
    emotion = request.GET.get("emotion")

    if assistant_slug:
        queryset = queryset.filter(linked_thought__assistant__slug=assistant_slug)

    if is_conversation in ["true", "1", "yes"]:
        queryset = queryset.filter(is_conversation=True)

    if project_id:
        queryset = queryset.filter(related_project_id=project_id)

    if emotion:
        queryset = queryset.filter(emotion=emotion)

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
@permission_classes([AllowAny])
def submit_memory_feedback(request):
    serializer = MemoryFeedbackSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save(
            submitted_by=request.user if request.user.is_authenticated else None
        )
        return Response(serializer.data, status=201)
    return Response(serializer.errors, status=400)


@api_view(["GET"])
def list_memory_feedback(request, memory_id):
    feedback = MemoryFeedback.objects.filter(memory_id=memory_id).order_by(
        "-created_at"
    )
    serializer = MemoryFeedbackSerializer(feedback, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([AllowAny])
def mutate_memory(request, id):
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
            tag_slugs = auto_tag_from_embedding(mutated) or []
            from mcp_core.models import Tag

            tag_objs = []
            for slug in tag_slugs:
                tag, _ = Tag.objects.get_or_create(slug=slug, defaults={"name": slug})
                tag_objs.append(tag)
            if tag_objs:
                new_mem.tags.add(*tag_objs)
    except Exception:
        pass

    if memory.assistant:
        log_assistant_thought(
            memory.assistant,
            f"Refined memory {memory.id} using style '{style}' based on feedback.",
            thought_type="meta",
            linked_memory=new_mem,
        )

    serializer = MemoryEntrySerializer(new_mem)
    return Response(serializer.data, status=201)


@api_view(["POST"])
@permission_classes([AllowAny])
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
@permission_classes([AllowAny])
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
    from memory.utils import normalize_tag_name

    data = request.data
    tag_names = data.pop("tags", [])

    if "event" not in data:
        return Response({"error": "Missing required field: event"}, status=400)

    memory = MemoryEntry.objects.create(
        event=data["event"],
        emotion=data.get("emotion"),
        importance=data.get("importance", 5),
        related_project=data.get("related_project"),
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
@permission_classes([AllowAny])
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
@permission_classes([AllowAny])
def update_memory_tags(request, id):
    from mcp_core.models import Tag
    from memory.utils import normalize_tag_name

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
@permission_classes([AllowAny])
def replace_memory(request, id):
    from mcp_core.models import Tag
    from memory.utils import normalize_tag_name

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
@permission_classes([AllowAny])
def assistant_memories(request, slug):
    try:
        assistant = Assistant.objects.get(slug=slug)
    except Assistant.DoesNotExist:
        return Response({"error": "Assistant not found"}, status=404)

    linked_thought_ids = AssistantThoughtLog.objects.filter(
        assistant=assistant
    ).values_list("linked_memory_id", flat=True)

    memories = MemoryEntry.objects.filter(id__in=linked_thought_ids).order_by(
        "-created_at"
    )
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
@permission_classes([AllowAny])
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
@permission_classes([AllowAny])
def shared_memory_pool_detail(request, pool_id):
    pool = get_object_or_404(SharedMemoryPool, id=pool_id)
    serializer = SharedMemoryPoolSerializer(pool)
    return Response(serializer.data)


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
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
