import logging
from images.models import Image, StableDiffusionUsageLog
from images.helpers.image_urls import generate_absolute_urls
from images.utils.thumbnails import generate_thumbnails
from images.helpers.prompt_helpers import enrich_prompt_tags
from images.helpers.download_utils import download_image
from tts.tasks import queue_tts_story

logger = logging.getLogger(__name__)


def trigger_post_generation_hook(image_id: int):
    try:
        image = Image.objects.get(id=image_id)
        logger.info(f"🪄 Triggered post-gen for Image {image.id}")

        # ✅ Generate thumbnail only if missing
        try:
            if image.style and image.style.image_path:
                logger.info(
                    f"🛑 Skipping thumbnail: already exists for style '{image.style.name}'"
                )
            else:
                generate_thumbnails(image)
        except Exception as e:
            logger.warning(f"🔍 Thumbnail failed for image {image.id}: {e}")

        # 🧠 Enrich tags from style presets
        try:
            enrich_prompt_tags(image)
        except Exception as e:
            logger.warning(f"📎 Tag enrichment failed: {e}")

        # 🔊 TTS story narration
        try:
            if image.prompt and image.user:
                queue_tts_story(image.prompt, user_id=image.user.id)
        except Exception as e:
            logger.warning(f"🎙️ TTS failed to trigger: {e}")

        # 🧬 Auto-upscale placeholder
        try:
            if image.width < 512 or image.height < 512:
                logger.info(f"⚡ Image {image.id} marked for upscale")
        except Exception as e:
            logger.warning(f"⚠️ Auto-upscale failed: {e}")

        # 📊 Log usage
        try:
            if image.user and image.prompt:
                StableDiffusionUsageLog.objects.create(
                    user=image.user,
                    image=image,
                    prompt=image.prompt,
                    estimated_credits_used=1,  # Update with your logic later
                )
        except Exception as e:
            logger.warning(f"📉 Failed to log Stability usage: {e}")

    except Image.DoesNotExist:
        logger.warning(f"⚠️ Post-gen hook failed: Image ID {image_id} not found.")
    except Exception as e:
        logger.error(f"🔥 Unexpected error in post-gen hook: {e}")
