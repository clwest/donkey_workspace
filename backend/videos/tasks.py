# videos/tasks.py
import logging
from celery import shared_task
from django.utils.timezone import now
from django.core.files.base import ContentFile
from .models import Video
from .utils.runway_api import generate_gen4_video_with_image

logger = logging.getLogger(__name__)


@shared_task
def generate_runway_video(video_id):
    try:
        video = Video.objects.get(id=video_id)
        video.status = "processing"
        video.save()

        logger.info(f"🎞️ Processing RunwayVideo {video_id}...")

        if not video.input_image:
            raise ValueError("Input image is required for Gen-4")

        video_bytes = generate_gen4_video_with_image(
            prompt=video.prompt or "Make it move magically!",
            image_path=video.input_image.path,
        )

        filename = f"video_{video.id}.mp4"
        video.video_file.save(filename, ContentFile(video_bytes))
        video.status = "completed"
        video.completed_at = now()
        video.save()

        logger.info(f"✅ Video saved for RunwayVideo {video_id}")

    except Exception as e:
        logger.exception(f"🔥 Runway video generation failed")
        if "video" in locals():
            video.status = "failed"
            video.save()
        return


# Dynamic routing of video generation tasks based on backend
@shared_task
def process_video_request(video_id):
    """
    Route video generation to the appropriate backend task.
    """
    from .models import Video
    from trainers.tasks import generate_kling_video_task

    video = Video.objects.get(id=video_id)
    if video.model_backend == "replicate-kling":
        generate_kling_video_task.delay(video.id)
    else:
        # Fallback to Runway Gen-4 pipeline
        generate_runway_video.delay(video.id)
