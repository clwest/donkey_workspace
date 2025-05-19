from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets, generics, status
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
import hashlib
from django.core.cache import cache
import logging
from openai import OpenAI
from .models import CharacterProfile
from rest_framework import status
from embeddings.vector_utils import compute_similarity
from embeddings.models import Embedding
from django.db import models
from characters.models import (
    CharacterProfile,
    CharacterStyle,
    CharacterReferenceImage,
    CharacterTrainingProfile,
)
from characters.serializers import (
    CharacterProfileSerializer,
    CharacterStyleSerializer,
    CharacterReferenceImageSerializer,
    CharacterTrainingProfileSerializer,
)
from rest_framework.decorators import action

# Scene generation: use core image generation tied to a character
from images.models import Image as SceneImage, PromptHelper as ScenePromptHelper
from images.tasks import process_sd_image_request
from django.shortcuts import get_object_or_404
from rest_framework.permissions import AllowAny


client = OpenAI()


class CharacterProfileViewSet(viewsets.ModelViewSet):
    queryset = CharacterProfile.objects.all()
    serializer_class = CharacterProfileSerializer
    # Use slug field for lookup instead of numeric ID
    lookup_field = "slug"

    def get_serializer_context(self):
        """
        Include request in serializer context to build absolute URLs for image fields.
        """
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def get_queryset(self):
        """
        Return character profiles ordered by creation date (newest first) to ensure
        consistent pagination results.
        """
        return CharacterProfile.objects.all().order_by("-created_at")

    @action(
        detail=True,
        methods=["post"],
        url_path="scene-edit",
        permission_classes=[AllowAny],
    )
    def scene_edit(self, request, slug=None):
        """
        Generate a new scene-based image for this character.
        POST data: { prompt: str, style_id: int (optional), base_image_id: int (optional) }
        """
        character = self.get_object()
        data = request.data
        prompt = data.get("prompt", "").strip()
        if not prompt:
            return Response(
                {"error": "Prompt is required"}, status=status.HTTP_400_BAD_REQUEST
            )
        # Optional theme enrichment
        neg_prompt = ""
        theme_id = data.get("theme_id")
        if theme_id:
            try:
                from images.models import ThemeHelper

                theme = ThemeHelper.objects.filter(id=theme_id).first()
                if theme and theme.prompt:
                    prompt = f"{prompt}, {theme.prompt.strip()}"
                if theme and theme.negative_prompt:
                    neg_prompt = theme.negative_prompt.strip()
            except Exception:
                pass
        # Resolve style if provided
        style = None
        style_id = data.get("style_id")
        if style_id:
            try:
                style = ScenePromptHelper.objects.get(id=style_id)
            except ScenePromptHelper.DoesNotExist:
                return Response(
                    {"error": "Invalid style_id"}, status=status.HTTP_400_BAD_REQUEST
                )
        # Base image handling (optional)
        # TODO: implement use of base_image_id for inpainting background
        # Create image generation request
        img_req = SceneImage.objects.create(
            user=request.user,
            character=character,
            prompt=prompt,
            description=prompt,
            negative_prompt=neg_prompt,
            width=512,
            height=512,
            order=0,
            steps=50,
            style=style,
            engine_used="stable-diffusion",
            status="queued",
            generation_type="scene",
        )
        # Queue generation task
        process_sd_image_request.delay(img_req.id)
        return Response(
            {
                "message": "Scene generation request queued.",
                "request_id": img_req.id,
                "status": img_req.status,
            },
            status=status.HTTP_201_CREATED,
        )


class CharacterStyleViewSet(viewsets.ModelViewSet):
    queryset = CharacterStyle.objects.all()
    serializer_class = CharacterStyleSerializer


import requests
import time
from django.core.files.base import ContentFile
from django.utils.text import slugify
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework import status
from rest_framework.response import Response


class CharacterReferenceImageViewSet(viewsets.ModelViewSet):
    """ViewSet to handle reference image uploads, including URL-based uploads."""

    queryset = CharacterReferenceImage.objects.all()
    serializer_class = CharacterReferenceImageSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    # Note: Use nested view (CharacterImagesView) to list by character

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        image_url = data.get("image")
        # If image is provided as URL string (no file upload), fetch and convert to file
        if image_url and "image" not in request.FILES:
            try:
                resp = requests.get(image_url)
                resp.raise_for_status()
                # Generate a filename: sd_preview_<slug>_<timestamp>.webp
                char_id = data.get("character") or data.get("character_id")
                # Attempt to get character name via queryset
                try:
                    from characters.models import CharacterProfile

                    char = CharacterProfile.objects.filter(id=char_id).first()
                    base = slugify(char.name) if char else "preview"
                except Exception:
                    base = "preview"
                filename = f"sd_preview_{base}_{int(time.time())}.webp"
                data["image"] = ContentFile(resp.content, name=filename)
            except Exception as e:
                return Response(
                    {"error": f"Failed to fetch image from URL: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        # Generate caption and alt_text from character info if not provided
        char_id = data.get("character") or data.get("character_id")
        character = None
        if char_id:
            try:
                character = CharacterProfile.objects.filter(id=char_id).first()
            except Exception:
                character = None
        # Build dynamic caption
        if not data.get("caption"):
            if character:
                traits = character.personality_traits or []
                traits_str = ", ".join(traits)
                desc = (character.description or "").strip()
                caption = f"Preview of {character.name}"
                if traits_str and desc:
                    caption += f" – a {traits_str} {desc.lower()}"
                elif traits_str:
                    caption += f" – a {traits_str} character"
                elif desc:
                    caption += f" – a {desc.lower()}"
            else:
                caption = "Autogenerated preview image"
            data["caption"] = caption
        # Build dynamic alt_text
        if not data.get("alt_text"):
            if character:
                traits = character.personality_traits or []
                traits_str = ", ".join(traits)
                desc = (character.description or "").strip()
                alt_text = f"AI-generated image of {character.name}"
                if desc:
                    alt_text += f" with {desc.lower()}"
                elif traits_str:
                    alt_text += f" with {traits_str}"
            else:
                alt_text = "Character preview image"
            data["alt_text"] = alt_text
        # Proceed with default creation
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        # Save the reference image
        self.perform_create(serializer)
        ref_image = serializer.instance
        # Trigger embedding training for the character
        try:
            from characters.tasks import train_character_embedding

            train_character_embedding.delay(ref_image.character.id)
        except Exception:
            pass
        # Generate and assign semantic tags for this reference image
        try:
            from images.models import TagImage

            character = ref_image.character
            tags = set()
            # Character name
            if character.name:
                tags.add(character.name.lower())
            # Personality traits
            for t in character.personality_traits or []:
                if isinstance(t, str) and t.strip():
                    tags.add(t.lower())
            # Description words longer than 4 chars
            for w in (character.description or "").split():
                w_clean = w.strip().lower()
                if len(w_clean) > 4:
                    tags.add(w_clean)
            # Create or get tag objects and assign
            tag_objs = []
            for name in tags:
                obj, _ = TagImage.objects.get_or_create(name=name)
                tag_objs.append(obj)
            ref_image.tags.set(tag_objs)
        except Exception:
            pass
        # Respond with created data
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )


class CharactersByProjectView(generics.ListAPIView):
    """
    List all CharacterProfile entries associated with a given Project.
    """

    serializer_class = CharacterProfileSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        project_id = self.kwargs.get("pk")
        return CharacterProfile.objects.filter(project_id=project_id)


# List reference images for a specific character
class CharacterImagesView(APIView):
    """Retrieve all reference images for a given character"""

    permission_classes = [AllowAny]

    def get(self, request, pk):
        """
        Retrieve all reference images for a given character.
        Returns list of images with id, url, caption, alt_text, and style_name (None for reference images).
        """
        character = get_object_or_404(CharacterProfile, pk=pk)
        images_data = []
        # Reference images
        for ref in character.reference_images.all():
            # Build full URL for image
            try:
                url = request.build_absolute_uri(ref.image.url)
            except Exception:
                url = ref.image.url
            images_data.append(
                {
                    "id": ref.id,
                    "url": url,
                    "caption": ref.caption or "",
                    "alt_text": ref.alt_text or "",
                    "style_name": None,
                }
            )
        return Response(images_data)


class NameGenerationView(APIView):
    """
    API endpoint to generate a character name based on description, backstory, and traits.
    """

    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        description = request.data.get("description", "")
        backstory = request.data.get("backstory", "")
        traits = request.data.get("traits", "")
        prompt_parts = []
        if description:
            prompt_parts.append(f"Description: {description}")
        if backstory:
            prompt_parts.append(f"Backstory: {backstory}")
        if traits:
            prompt_parts.append(f"Personality Traits: {traits}")
        if not prompt_parts:
            return Response(
                {"error": "Provide description, backstory, or traits."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        prompt = (
            "Suggest a creative and unique character name for the following details. "
            "Provide only the name without additional commentary.\n\n"
            + "\n".join(prompt_parts)
        )
        try:
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=20,
                temperature=0.8,
                n=1,
            )
            content = resp.choices[0].message.content.strip()
            name = content.strip('"').strip()
            return Response({"name": name}, status=status.HTTP_200_OK)
        except Exception as e:
            logging.getLogger(__name__).error("Name generation failed", exc_info=e)
            return Response(
                {"error": f"Name generation failed: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CharacterSimilarityView(APIView):
    """
    Compute semantic similarity between input text and existing characters.
    Returns top 5 matches (public or owned by user).
    """

    permission_classes = [AllowAny]

    def post(self, request):
        text = request.data.get("text", "").strip()
        if not text:
            return Response(
                {"error": "No text provided."}, status=status.HTTP_400_BAD_REQUEST
            )
        # Handle cache toggle
        nocache = request.query_params.get("nocache") == "true"
        # Compute fingerprint for caching
        try:
            fingerprint = hashlib.sha256(text.encode("utf-8")).hexdigest()
            cache_key = f"char-sim:{fingerprint}"
        except Exception:
            fingerprint = None
            cache_key = None
        logger = logging.getLogger("django")
        # Attempt cache lookup
        if not nocache and cache_key:
            try:
                cached = cache.get(cache_key)
                if cached is not None:
                    logger.info(f"Cache hit for key {cache_key}")
                    return Response(cached)
            except Exception as e:
                logger.warning(f"Cache get error for {cache_key}: {e}")
        logger.info(f"Cache miss for key {cache_key}")
        # Generate embedding and compute similarity safely
        try:
            from embeddings.helpers.helpers_processing import generate_embedding
            from embeddings.vector_utils import compute_similarity
        except ImportError:
            return Response([], status=status.HTTP_200_OK)
        try:
            embedding = generate_embedding(text)
            if not embedding:
                raise ValueError("Failed to generate embedding")
            # Find similar characters by comparing to each character's stored embedding
            results = []
            from embeddings.models import Embedding

            user = request.user
            qs = CharacterProfile.objects.filter(
                models.Q(is_public=True) | models.Q(created_by=user)
            )
            for char in qs:
                try:
                    emb_rec = (
                        Embedding.objects.filter(
                            content_type="characterprofile", content_id=str(char.id)
                        )
                        .order_by("-created_at")
                        .first()
                    )
                    if not emb_rec:
                        continue
                    score = compute_similarity(embedding, emb_rec.embedding)
                    results.append({"id": char.id, "name": char.name, "score": score})
                except Exception as e:
                    logging.getLogger("django").error(
                        f"Error computing similarity for character {char.id}: {e}",
                        exc_info=True,
                    )
                    continue
            # sort and take top 5
            results.sort(key=lambda x: x["score"], reverse=True)
            top5 = results[:5]
            # Store in cache
            if not nocache and cache_key:
                try:
                    cache.set(cache_key, top5, timeout=24 * 3600)
                    logging.getLogger("django").info(
                        f"Cached similarity results under key {cache_key}"
                    )
                except Exception as e:
                    logging.getLogger("django").warning(
                        f"Cache set error for {cache_key}: {e}"
                    )
            return Response(top5)
        except Exception as e:
            logging.getLogger("django").error(
                f"Error in CharacterSimilarityView: {e}", exc_info=True
            )
            # Safe fallback: return empty list instead of server error
            return Response([], status=status.HTTP_200_OK)


class CharacterTrainingStatusView(APIView):
    """Retrieve the training profile for a given character."""

    permission_classes = [AllowAny]

    def get(self, request, pk):
        """Return the training profile for a specific character, creating if missing."""
        # Ensure the character exists
        character = get_object_or_404(CharacterProfile, pk=pk)
        # Get or create the training profile
        training, _created = CharacterTrainingProfile.objects.get_or_create(
            character=character
        )
        serializer = CharacterTrainingProfileSerializer(training)
        return Response(serializer.data)


class CharacterProfileSimilarityView(APIView):
    """Retrieve top similar characters to the given character based on stored embeddings."""

    permission_classes = [AllowAny]

    def get(self, request, pk):
        """Return top similar characters for a given character based on stored embeddings."""
        # Ensure the character exists
        profile = get_object_or_404(CharacterProfile, pk=pk)
        # Ensure training profile exists
        training, _created = CharacterTrainingProfile.objects.get_or_create(
            character=profile
        )
        embedding = getattr(training, "embedding", None)
        if not embedding:
            # No embeddings yet; return empty list
            return Response([], status=status.HTTP_200_OK)
        try:
            from embeddings.helpers.helpers_processing import find_similar_characters

            # Retrieve similar entries (id and score)
            entries = find_similar_characters(embedding, top_k=5) or []
            results = []
            for entry in entries:
                char_id = entry.get("id")
                score = entry.get("score")
                # Skip invalid or self
                if not char_id or char_id == pk or score is None:
                    continue
                try:
                    char = CharacterProfile.objects.get(pk=char_id)
                except CharacterProfile.DoesNotExist:
                    continue
                results.append(
                    {
                        "id": char.id,
                        "name": char.name,
                        "score": score,
                    }
                )
            return Response(results)
        except Exception as e:
            logging.getLogger("django").error(
                f"Error in CharacterProfileSimilarityView: {e}", exc_info=True
            )
            # Safe fallback: return empty list
            return Response([], status=status.HTTP_200_OK)


# Endpoint to trigger embedding training via Celery
class CharacterTrainView(APIView):
    """Trigger embedding training for a given character via Celery task."""

    permission_classes = [AllowAny]

    def post(self, request, pk):
        try:
            from django.shortcuts import get_object_or_404
            from characters.models import CharacterProfile
            from characters.tasks import train_character_embedding

            profile = get_object_or_404(CharacterProfile, pk=pk)
            # Schedule training task asynchronously
            task = train_character_embedding.delay(pk)
            return Response({"task_id": task.id}, status=status.HTTP_202_ACCEPTED)
        except Exception as e:
            logging.getLogger("django").error(
                f"Error in CharacterTrainView: {e}", exc_info=True
            )
            return Response(
                {"error": "Failed to trigger training"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class CharactersByProjectView(generics.ListAPIView):
    """
    List all CharacterProfile entries associated with a given Project.
    """

    serializer_class = CharacterProfileSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        project_id = self.kwargs.get("pk")
        return CharacterProfile.objects.filter(project_id=project_id)
