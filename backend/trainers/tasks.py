from celery import shared_task
from django.contrib.auth import get_user_model
from django.conf import settings

from .models import ReplicatePrediction, ReplicateModel
from .helpers.replicate_helpers import generate_image, get_prediction_detail
import requests
from .helpers.trainers_logic import perform_clear_and_optimize_image

User = settings.AUTH_USER_MODEL


@shared_task
def generate_prediction_task(
    user_id: int, model_id: int, prompt: str, require_trigger_word: bool = True
) -> int:
    """
    Task to generate a new prediction via Replicate and save to database.
    Returns the primary key of the created ReplicatePrediction.
    """
    user = get_user_model().objects.get(pk=user_id)
    model = ReplicateModel.objects.get(pk=model_id)
    # Call external service
    prediction = generate_image(prompt, require_trigger_word)
    # Create local record
    obj = ReplicatePrediction.objects.create(
        user=user,
        model=model,
        prediction_id=prediction.id,
        prompt=prompt,
        status=prediction.status,
        num_outputs=(
            prediction.input.get("num_outputs")
            if hasattr(prediction, "input")
            else None
        )
        or 1,
    )
    return obj.pk


@shared_task
def poll_prediction_status_task(prediction_pk: int) -> str:
    """
    Task to poll Replicate API for updated status and outputs, then update DB.
    Returns the updated status string.
    """
    try:
        obj = ReplicatePrediction.objects.get(pk=prediction_pk)
    except ReplicatePrediction.DoesNotExist:
        return "not_found"
    data, code = get_prediction_detail(obj.prediction_id)
    if data is None:
        obj.status = "failed"
        obj.save()
        return obj.status
    # Update fields
    obj.status = data.status
    obj.files = data.output or [] if hasattr(data, "output") else obj.files
    if hasattr(data, "started_at"):
        obj.started_at = data.started_at
    if hasattr(data, "completed_at"):
        obj.completed_at = data.completed_at
    obj.save()
    return obj.status


@shared_task
def download_prediction_files_task(prediction_pk: int) -> int:
    """
    Task to download generated files from external URLs and optimize them locally.
    Returns number of successfully downloaded files.
    """
    try:
        obj = ReplicatePrediction.objects.get(pk=prediction_pk)
    except ReplicatePrediction.DoesNotExist:
        return 0
    count = 0
    for idx, url in enumerate(obj.files or []):
        try:
            # Fetch raw file content via HTTP
            response = requests.get(url)
            if response.status_code != 200:
                continue
            content = response.content
            # Write to temporary path and optimize
            temp_path = f"data/generated/{obj.prediction_id}_{idx}.jpg"
            with open(temp_path, "wb") as f:
                f.write(content)
            # Validate and optimize image
            perform_clear_and_optimize_image(temp_path, temp_path)
            count += 1
        except Exception:
            continue
    return count


@shared_task
def generate_kling_video_task(video_id):
    """
    Generate a video using the Replicate Kling v1.6 model and enqueue prediction.
    """
    from trainers.helpers.replicate_helpers import get_replicate_client
    from trainers.helpers.replicate_router import get_model_info
    from videos.models import Video
    import logging

    logger = logging.getLogger("django")

    video = Video.objects.get(id=video_id)
    model_slug, version_id = get_model_info(video.model_backend)

    client = get_replicate_client()
    model = client.models.get(model_slug)
    version = model.versions.get(version_id)

    try:
        prediction = client.predictions.create(
            version=version,
            input={
                "prompt": video.prompt,
                "num_frames": 24,
                "output_format": "mp4",
            },
        )
        video.prediction_id = prediction.id
        video.status = "queued"
        video.save()
    except Exception as e:
        video.status = "failed"
        video.error_message = str(e)
        video.save()
        logger.error(f"❌ Kling video generation failed: {e}")
