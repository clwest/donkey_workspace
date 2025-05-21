from rest_framework import viewsets, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action, api_view
from django.utils.timezone import now
from .models import Story, NarrativeEvent
from .serializers import (
    StorySerializer,
    StoryDetailSerializer,
    NarrativeEventSerializer,
)
from story.tasks import generate_story_task, embed_story_chunks
from story.utils.story_generation import create_full_story_with_media
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework.views import APIView


class StoryViewSet(viewsets.ModelViewSet):
    queryset = Story.objects.all().order_by("-created_at")
    serializer_class = StorySerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["prompt", "theme", "tags"]
    ordering_fields = ["created_at", "updated_at"]

    def get_queryset(self):
        """
        Optionally filter stories by character_id query param.
        """
        if not self.request.user.is_authenticated:
            return Story.objects.none()
        qs = Story.objects.filter(user=self.request.user).order_by("-created_at")
        char_id = self.request.query_params.get("character")
        if char_id:
            qs = qs.filter(characters__id=char_id)
        return qs

    def get_serializer_class(self):
        if self.action == "retrieve":
            return StoryDetailSerializer
        return StorySerializer

    def perform_create(self, serializer):
        story = serializer.save(user=self.request.user)
        generate_story_task.delay(story.id)

    def create(self, request, *args, **kwargs):
        """
        Custom create to return serialized story after queuing.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        story = serializer.save(user=request.user)
        generate_story_task.delay(story.id)

        # Return the full serialized story object
        response_serializer = self.get_serializer(story)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["post"], url_path="retry")
    def retry_generation(self, request, pk=None):
        try:
            story = self.get_queryset().get(id=pk)

            if story.generated_text:
                return Response({"error": "Story already completed."}, status=400)

            story.updated_at = now()
            story.save()

            generate_story_task.delay(story.id)

            return Response(
                {
                    "message": f"Story {story.id} re-queued for generation.",
                    "status": "queued",
                },
                status=202,
            )

        except Story.DoesNotExist:
            return Response({"error": "Story not found."}, status=404)

    @action(
        detail=True,
        methods=["post"],
        url_path="audio",
        permission_classes=[AllowAny],
    )
    def generate_audio(self, request, pk=None):
        """
        Trigger TTS generation for the full story text and attach audio to the Story.
        """
        try:
            story = self.get_queryset().get(id=pk)
        except Story.DoesNotExist:
            return Response({"error": "Story not found."}, status=404)
        # Use generated_text if available, otherwise fallback to prompt
        text = story.generated_text or story.prompt or ""
        if not text:
            return Response({"error": "No story text available for TTS."}, status=400)
        # Create a StoryAudio record linked to this story
        from tts.models import StoryAudio
        from tts.tasks import queue_tts_story
        from tts.serializers import StoryAudioSerializer

        audio_obj = StoryAudio.objects.create(
            story=story,
            project=story.project,
            user=request.user,
            prompt=text,
            voice_style=request.data.get("voice_style", None),
            provider=request.data.get("provider", StoryAudio.TTS_PROVIDERS[0][0]),
            status="queued",
        )
        # Enqueue the TTS task
        queue_tts_story.delay(
            prompt_text=text,
            user_id=request.user.id,
            voice=audio_obj.voice_style or None,
            provider=audio_obj.provider or None,
        )
        # Return the initial audio record
        serializer = StoryAudioSerializer(audio_obj, context={"request": request})
        return Response(serializer.data, status=status.HTTP_202_ACCEPTED)

    @action(
        detail=True,
        methods=["post"],
        url_path="tag-chunks",
        permission_classes=[AllowAny],
    )
    def tag_chunks(self, request, pk=None):
        """
        Trigger paragraph-level embedding + tag inference for the story.
        """
        try:
            story = self.get_queryset().get(id=pk)
        except Story.DoesNotExist:
            return Response(
                {"error": "Story not found."}, status=status.HTTP_404_NOT_FOUND
            )
        embed_story_chunks.delay(story.id)
        return Response({"queued": True}, status=status.HTTP_202_ACCEPTED)

    @action(
        detail=True,
        methods=["get"],
        url_path="chunk-tags",
        permission_classes=[AllowAny],
    )
    def chunk_tags(self, request, pk=None):
        """
        List the tags inferred for each paragraph chunk of the story.
        """
        try:
            story = self.get_queryset().get(id=pk)
        except Story.DoesNotExist:
            return Response(
                {"error": "Story not found."}, status=status.HTTP_404_NOT_FOUND
            )
        from embeddings.models import StoryChunkEmbedding

        chunks = StoryChunkEmbedding.objects.filter(story=story).order_by(
            "paragraph_index"
        )
        data = []
        for c in chunks:
            data.append(
                {
                    "paragraph_index": c.paragraph_index,
                    "text": c.text,
                    "tags": [t.name for t in c.tags.all()],
                }
            )
        return Response(data)

    @action(
        detail=True,
        methods=["get"],
        url_path="tags",
        permission_classes=[AllowAny],
    )
    def tags(self, request, pk=None):
        """
        Aggregate all chunk-level inferred tags for the story and return top 5 by frequency.
        """
        from embeddings.models import StoryChunkEmbedding
        from collections import Counter

        try:
            story = self.get_queryset().get(id=pk)
        except Story.DoesNotExist:
            return Response(
                {"error": "Story not found."}, status=status.HTTP_404_NOT_FOUND
            )

        # Gather all tags from each chunk embedding
        chunks = StoryChunkEmbedding.objects.filter(story=story)
        tag_counts = Counter()
        for chunk in chunks:
            # chunk.tags is ManyToMany of TagConcept
            tag_counts.update([t.name for t in chunk.tags.all()])

        # Get top 5 most common tags
        top = [tag for tag, _ in tag_counts.most_common(5)]

        return Response(
            {
                "story_id": story.id,
                "top_tags": top,
            }
        )


"""
ViewSet for listing and creating stories under a specific project.
"""
from rest_framework.permissions import AllowAny


class ProjectStoriesViewSet(viewsets.ModelViewSet):
    """
    Manages Story objects scoped to a parent Project (project_pk URL kwarg).
    """

    serializer_class = StorySerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        # Only stories belonging to the specified project and user
        return Story.objects.filter(
            project_id=self.kwargs.get("project_pk"), user=self.request.user
        ).order_by("-created_at")

    def perform_create(self, serializer):
        # Attach the project and user when creating
        serializer.save(
            project_id=self.kwargs.get("project_pk"), user=self.request.user
        )


class StoryCreateView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data
        user = request.user

        project = None
        if data.get("project_id"):
            from project.models import Project

            project = Project.objects.filter(id=data["project_id"], user=user).first()

        story = create_full_story_with_media(
            user=user,
            prompt=data["prompt"],
            theme=data.get("theme"),
            tags=data.get("tags", []),
            image_style=data.get("image_style"),
            narrator_voice=data.get("narrator_voice"),
            project=project,
            is_reward=data.get("is_reward", False),
            reward_reason=data.get("reward_reason"),
        )

        return Response(
            {
                "message": "📖 Story creation started!",
                "story_id": story.id,
                "status": story.status,
                "image_caption": story.image_caption,
                "image_alt_text": story.image_alt_text,
            },
            status=status.HTTP_201_CREATED,
        )


@api_view(["GET"])
def storyboard_list(request):
    """Return all narrative events for selection."""
    events = NarrativeEvent.objects.all().order_by("-timestamp")
    serializer = NarrativeEventSerializer(events, many=True)
    return Response(serializer.data)
