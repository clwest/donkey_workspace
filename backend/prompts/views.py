from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from django.shortcuts import get_object_or_404
import logging
from prompts.models import Prompt, PromptPreferences
from prompts.serializers import PromptSerializer, PromptPreferencesSerializer
from mcp_core.models import Tag
from mcp_core.serializers_tags import TagSerializer
from prompts.utils.embeddings import get_prompt_embedding
from prompts.utils.token_helpers import smart_chunk_prompt, count_tokens
from prompts.utils.auto_reduce import auto_reduce_prompt
from prompts.utils.mutation import mutate_prompt as run_mutation
from prompts.utils.openai_utils import (
    reduce_tokens,
    generate_prompt_from_idea,
    extract_title_from_prompt,
)
from mcp_core.utils.log_prompt import log_prompt_usage

logger = logging.getLogger("prompts")
from assistants.models.assistant import Assistant
from django.db import connection, models
import textstat

from mcp_core.models import PromptUsageLog
from mcp_core.serializers import PromptUsageLogSerializer


@api_view(["GET"])
@permission_classes([AllowAny])
def list_prompts(request):
    query = request.query_params.get("q")
    show_all = request.query_params.get("show_all", "false").lower() == "true"
    sort = request.query_params.get("sort", "created")
    type_filter = request.query_params.get("type")

    prompts = Prompt.objects.none()

    if query:
        vector = get_prompt_embedding(query)
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT id, embedding <#> %s::vector AS score
                FROM prompts_prompt
                ORDER BY embedding <#> %s::vector
                LIMIT 20
                """,
                [vector, vector],
            )
            ids = [row[0] for row in cursor.fetchall()]
        prompts = Prompt.objects.filter(id__in=ids)

    elif show_all or type_filter:
        prompts = Prompt.objects.all()
        if sort == "tokens":
            prompts = prompts.order_by("-token_count")
        else:
            prompts = prompts.order_by("-created_at")

    if type_filter:
        prompts = prompts.filter(type=type_filter)

    serializer = PromptSerializer(prompts, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def prompt_search(request):
    """Simple title search for prompts."""
    term = request.GET.get("search") or request.GET.get("q")
    if not term:
        return Response([])
    qs = Prompt.objects.filter(title__icontains=term)[:20]
    return Response(PromptSerializer(qs, many=True).data)


@api_view(["POST"])
@permission_classes([AllowAny])
def create_prompt(request):
    serializer = PromptSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    prompt = serializer.save()

    # ✅ Fallback token count if not explicitly passed
    if not prompt.token_count:
        from prompts.utils.token_helpers import count_tokens

        prompt.token_count = count_tokens(prompt.content)
        prompt.save(update_fields=["token_count"])

    # ✅ Log usage (skip if saving as draft)
    if not request.data.get("is_draft", False):
        log_prompt_usage(
            prompt=prompt,
            used_by="api.prompts.create",
            purpose="manual_create",
            input_context=request.data.get("content", ""),
            rendered_prompt=prompt.content,
            result_output="",
        )

    return Response(PromptSerializer(prompt).data, status=201)


@api_view(["GET"])
def prompt_detail(request, slug):
    try:
        prompt = Prompt.objects.get(slug=slug)
    except Prompt.DoesNotExist:
        return Response({"error": "Prompt not found"}, status=404)

    serializer = PromptSerializer(prompt)
    return Response(serializer.data)


@api_view(["PATCH"])
def update_prompt(request, slug):
    try:
        prompt = Prompt.objects.get(slug=slug)
    except Prompt.DoesNotExist:
        return Response({"error": "Prompt not found"}, status=404)

    serializer = PromptSerializer(prompt, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    updated_prompt = serializer.save()
    logger.info("Prompt %s updated", slug)
    return Response(PromptSerializer(updated_prompt).data)


@api_view(["DELETE"])
def delete_prompt(request, slug):
    try:
        prompt = Prompt.objects.get(slug=slug)
    except Prompt.DoesNotExist:
        return Response({"error": "Prompt not found"}, status=404)

    force = request.query_params.get("force") == "true" or request.data.get("force")

    in_use = Assistant.objects.filter(system_prompt=prompt).exists()
    from prompts.models import PromptMutationLog

    history = PromptMutationLog.objects.filter(
        models.Q(original_prompt=prompt)
        | models.Q(mutated_prompt=prompt)
        | models.Q(source_prompt=prompt)
    ).exists()

    if (in_use or history) and not force:
        return Response({"error": "Prompt in use"}, status=400)

    prompt.delete()
    logger.info("Prompt %s deleted", slug)
    return Response(status=204)


@api_view(["POST"])
@permission_classes([AllowAny])
def generate_prompt_from_idea_view(request):
    goal = request.data.get("goal", "")
    audience = request.data.get("audience", "")
    tone = request.data.get("tone", "")
    key_points = request.data.get("key_points", "")

    if not goal:
        return Response({"error": "Missing goal input."}, status=400)

    messy_idea = (
        f"Goal: {goal}\nAudience: {audience}\nTone: {tone}\nKey Points: {key_points}"
    )
    result = generate_prompt_from_idea(messy_idea)

    # 🧠 Generate a basic title from first line or fallback
    title = extract_title_from_prompt(result) or f"Prompt for: {goal[:50]}..."

    # 🧮 Token count helper
    from prompts.utils.token_helpers import count_tokens

    token_count = count_tokens(result)

    # ✅ Save to DB
    prompt = Prompt.objects.create(
        title=title,
        content=result,
        source="assistant-idea-generator",
        type="idea",
        tone=tone or "neutral",
        token_count=token_count,
    )

    # 📦 Log usage with real FK
    log_prompt_usage(
        prompt=prompt,
        used_by="api.prompts.generate-from-idea",
        purpose="generate_idea",
        input_context=messy_idea,
        rendered_prompt=result,
        result_output=result,
    )

    return Response(PromptSerializer(prompt).data, status=201)


@api_view(["GET"])
def list_prompt_tags(request):
    tags = Tag.objects.all().order_by("name")
    serializer = TagSerializer(tags, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def list_mutation_styles(request):
    from prompts.mutation_styles import list_styles

    return Response(list_styles())


@api_view(["GET"])
@permission_classes([AllowAny])
def get_my_prompt_preferences(request):
    pref, _ = PromptPreferences.objects.get_or_create(user=request.user)
    serializer = PromptPreferencesSerializer(pref)
    return Response(serializer.data)


@api_view(["PATCH"])
@permission_classes([AllowAny])
def update_my_prompt_preferences(request):
    pref, _ = PromptPreferences.objects.get_or_create(user=request.user)
    serializer = PromptPreferencesSerializer(pref, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@api_view(["POST"])
def reduce_prompt(request):
    text = request.data.get("text", "")
    reduced = reduce_tokens(text)
    return Response({"text": reduced})


@api_view(["POST"])
def split_prompt(request):
    text = request.data.get("text", "")
    chunks = smart_chunk_prompt(text)
    return Response({"chunks": chunks})


@api_view(["POST"])
def auto_reduce_prompt_view(request):
    text = request.data.get("text", "")
    if not text:
        return Response({"error": "No text provided."}, status=400)

    reduced = auto_reduce_prompt(text)
    return Response({"text": reduced})


@api_view(["POST"])
def analyze_prompt(request):
    text = request.data.get("text", "")
    if not text:
        return Response({"error": "No text provided"}, status=400)

    analysis = {
        "tokens": len(text.split()),
        "flesch_reading_ease": textstat.flesch_reading_ease(text),
        "flesch_kincaid_grade": textstat.flesch_kincaid_grade(text),
        "avg_sentence_length": textstat.avg_sentence_length(text),
        "avg_syllables_per_word": textstat.avg_syllables_per_word(text),
        "reading_time_seconds": int(textstat.reading_time(text) * 60),
    }
    return Response(analysis)


@api_view(["POST"])
@permission_classes([AllowAny])
def mutate_prompt_view(request):
    text = request.data.get("text")
    mutation_type = request.data.get("mutation_type") or request.data.get("mode")
    tone = request.data.get("tone")
    prompt_id = request.data.get("prompt_id")

    if not text:
        logger.warning("mutate_prompt_view called with empty text")
        return Response({"error": "Missing text"}, status=400)

    missing_fields = []
    if not mutation_type:
        missing_fields.append("mutation_type")
    if not prompt_id:
        missing_fields.append("prompt_id")
    if not tone:
        missing_fields.append("tone")
    if missing_fields:
        return Response(
            {"error": f"Missing fields: {', '.join(missing_fields)}"}, status=400
        )

    result = run_mutation(text, mutation_type, prompt_id=prompt_id, tone=tone)

    if prompt_id:
        try:
            prompt_obj = Prompt.objects.get(id=prompt_id)
            log_prompt_usage(
                prompt=prompt_obj,
                used_by="mutation_tool",
                purpose="variant",
                context_id=str(prompt_id),
                input_context=text,
                rendered_prompt=result,
                result_output=result,
            )
        except Prompt.DoesNotExist:
            print(f"⚠️ Prompt not found for ID: {prompt_id}")

    return Response({"result": result})


@api_view(["POST"])
def reembed_all_prompts(request):
    prompts = Prompt.objects.all()
    updated = 0

    for prompt in prompts:
        try:
            embedding = get_prompt_embedding(prompt.content)
            prompt.embedding = embedding
            prompt.save()
            updated += 1
        except Exception as e:
            print(f"Failed to embed prompt {prompt.id}: {e}")

    return Response({"reembedded": updated})


@api_view(["POST"])
@permission_classes([AllowAny])
def assign_prompt_to_assistant(request, slug):
    prompt = get_object_or_404(Prompt, slug=slug)
    assistant_id = request.data.get("assistant_id")

    from utils.resolvers import resolve_or_error
    from django.core.exceptions import ObjectDoesNotExist

    try:
        assistant = resolve_or_error(assistant_id, Assistant)
    except ObjectDoesNotExist:
        return Response({"error": "Assistant not found"}, status=404)

    assistant.system_prompt = prompt
    assistant.save()
    return Response({"status": "assigned"}, status=200)


@api_view(["GET"])
@permission_classes([AllowAny])
def prompt_usage_logs_view(request, slug):
    logs = PromptUsageLog.objects.filter(prompt__slug=slug).order_by("-created_at")
    serializer = PromptUsageLogSerializer(logs, many=True)
    return Response(serializer.data)


from rest_framework import viewsets
from .models import PromptCapsule, CapsuleTransferLog
from .serializers import PromptCapsuleSerializer, CapsuleTransferLogSerializer


class PromptCapsuleViewSet(viewsets.ModelViewSet):
    queryset = PromptCapsule.objects.all().order_by("-created_at")
    serializer_class = PromptCapsuleSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        assistant = self.request.GET.get("assistant")
        tag = self.request.GET.get("tag")
        if assistant:
            qs = qs.filter(transfers__to_assistant_id=assistant).distinct()
        if tag:
            qs = qs.filter(tags__slug=tag).distinct()
        return qs


class CapsuleTransferLogViewSet(viewsets.ModelViewSet):
    queryset = CapsuleTransferLog.objects.all().order_by("-created_at")
    serializer_class = CapsuleTransferLogSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        assistant = self.request.GET.get("assistant")
        if assistant:
            qs = qs.filter(to_assistant_id=assistant)
        return qs


@api_view(["GET"])
@permission_classes([AllowAny])
def validate_prompt_links(request):
    """Return system prompts missing documents or unused by assistants."""
    unlinked_prompts = list(
        Prompt.objects.filter(type="system", source_document__isnull=True).values(
            "id",
            "slug",
            "title",
        )
    )

    from intel_core.models import Document

    orphan_documents = list(
        Document.objects.filter(prompts__isnull=True).values("id", "slug", "title")
    )

    unused_prompts = list(
        Prompt.objects.filter(
            type="system", assistants_using_prompt__isnull=True
        ).values("id", "slug", "title")
    )

    return Response(
        {
            "unlinked_prompts": unlinked_prompts,
            "orphan_documents": orphan_documents,
            "unused_prompts": unused_prompts,
        }
    )
