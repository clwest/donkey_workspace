# videos/views.py

from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Video
from .serializers import VideoSerializer
from .tasks import process_video_request


class VideoViewSet(viewsets.ModelViewSet):
    queryset = Video.objects.all().order_by("-created_at")
    serializer_class = VideoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        video = serializer.save(user=self.request.user, status="queued")
        process_video_request.delay(video.id)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(
            {
                "message": "Video generation queued",
                "status": "queued",
            },
            status=status.HTTP_202_ACCEPTED,
        )

    @action(detail=True, methods=["post"], url_path="retry")
    def retry_failed(self, request, pk=None):
        try:
            video = self.get_queryset().get(id=pk, user=request.user)
            if video.status != "failed":
                return Response(
                    {"error": "Only failed videos can be retried."}, status=400
                )

            video.status = "queued"
            video.video_file = None
            video.video_url = None
            video.error_message = None
            video.save()

            process_video_request.delay(video.id)
            return Response(
                {"message": f"Video {video.id} re-queued.", "status": "queued"},
                status=202,
            )

        except Video.DoesNotExist:
            return Response({"error": "Video not found."}, status=404)

    @action(detail=False, methods=["post"], url_path="batch-generate")
    def batch_generate(self, request):
        """
        Batch generate videos for each paragraph in a story.
        """
        user = request.user
        story_id = request.data.get("story_id")
        model_backend = request.data.get("model_backend")
        prompt_override = request.data.get("prompt_override")
        if not story_id or not model_backend:
            return Response(
                {"error": "story_id and model_backend are required"}, status=400
            )
        from story.models import Story

        try:
            story = Story.objects.get(id=story_id)
        except Story.DoesNotExist:
            return Response({"error": "Story not found."}, status=404)
        # Split story text into paragraphs (separated by blank lines)
        paragraphs = [p for p in story.generated_text.split("\n\n") if p.strip()]
        created_ids = []
        for idx, para in enumerate(paragraphs):
            prompt = prompt_override or para
            video = Video.objects.create(
                user=user,
                story=story,
                prompt=prompt,
                model_backend=model_backend,
                status="queued",
                paragraph_index=idx,
            )
            process_video_request.delay(video.id)
            created_ids.append(video.id)
        return Response(
            {"status": "queued", "count": len(created_ids), "video_ids": created_ids},
            status=202,
        )
