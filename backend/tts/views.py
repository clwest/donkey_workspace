from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from tts.utils.elevenlabs_voices import get_elevenlabs_voices
from rest_framework.decorators import action
from rest_framework import filters
from .models import StoryAudio
from .serializers import StoryAudioSerializer
from tts.tasks import queue_tts_story


class StoryAudioViewSet(viewsets.ModelViewSet):
    queryset = StoryAudio.objects.all().order_by("-created_at")
    serializer_class = StoryAudioSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["prompt", "voice_style", "provider"]
    ordering_fields = ["created_at", "status", "voice_style"]

    def perform_create(self, serializer):
        # Save the object first with queued status
        story = serializer.save(user=self.request.user, status="queued")

        # Pull voice/provider from request data
        voice = self.request.data.get("voice_style", "echo")
        provider = self.request.data.get("provider", "openai")

        # Trigger async generation
        queue_tts_story.delay(
            prompt_text=story.prompt,
            user_id=self.request.user.id,
            voice=voice,
            provider=provider,
        )

    def create(self, request, *args, **kwargs):
        """
        Custom create to return job info instead of the full StoryAudio right away.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        return Response(
            {
                "message": "TTS generation request accepted.",
                "status": "queued",
            },
            status=status.HTTP_202_ACCEPTED,
        )

    @action(detail=True, methods=["post"], url_path="retry")
    def retry_failed(self, request, pk=None):
        try:
            story = self.get_queryset().get(id=pk, user=request.user)

            if story.status != "failed":
                return Response(
                    {"error": "Only failed TTS jobs can be retried."}, status=400
                )

            story.status = "queued"
            story.audio_file = None
            story.base64_audio = None
            story.save()

            queue_tts_story.delay(
                prompt_text=story.prompt,
                user_id=request.user.id,
                voice=story.voice_style or "echo",
                provider=story.provider or "openai",
            )

            return Response(
                {"message": f"TTS job {story.id} re-queued.", "status": "queued"},
                status=202,
            )

        except StoryAudio.DoesNotExist:
            return Response({"error": "TTS request not found."}, status=404)


class ElevenLabsVoiceViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]

    @action(detail=False, methods=["get"], url_path="list")
    def list_voices(self, request):
        """
        Returns available ElevenLabs voices with name, id, and labels.
        """
        try:
            voices = get_elevenlabs_voices()
            return Response(voices)
        except Exception as e:
            return Response({"error": str(e)}, status=500)
