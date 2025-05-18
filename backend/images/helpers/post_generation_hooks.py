import logging
from images.models import Image
from images.helpers.image_urls import generate_absolute_urls
from images.utils.thumbnails import generate_thumbnails
from images.helpers.prompt_helpers import enrich_prompt_tags
from images.helpers.download_utils import download_image
from tts.tasks import queue_tts_story  # optional TTS

# from runway.tasks import queue_video_generation  # future

logger = logging.getLogger(__name__)


def trigger_post_generation_hook(image_id: int):
    try:
        image = Image.objects.get(id=image_id)
        logger.info(f"🪄 Triggered post-gen for Image {image.id}")

        # 🌟 Generate thumbnail
        # 🌟 Generate thumbnail only if missing
        try:
            if image.style and image.style.image_path:
                logger.info(
                    f"🛑 Skipping thumbnail: already exists for style '{image.style.name}'"
                )
            else:
                generate_thumbnails(image)
        except Exception as e:
            logger.warning(f"🔍 Thumbnail generation failed for image {image.id}: {e}")

        # 🧠 Enrich tags from style presets (optional, can seed more tags for filtering/search)
        try:
            enrich_prompt_tags(image)
        except Exception as e:
            logger.warning(f"📎 Tag enrichment failed: {e}")

        # 🔊 Trigger TTS story narration
        try:
            if image.prompt and image.user:
                queue_tts_story(image.prompt, user_id=image.user.id)
        except Exception as e:
            logger.warning(f"🎙️ TTS failed to trigger: {e}")

        # 🧬 Auto-upscale if needed
        try:
            if image.width < 512 or image.height < 512:
                logger.info(f"⚡ Image {image.id} marked for upscale")
                # You'll want to eventually define `process_upscale_image_request.delay(...)`
        except Exception as e:
            logger.warning(f"⚠️ Auto-upscale failed: {e}")

        # 🎬 Future Gen-4 video generation
        # if image.style and image.style.name.lower() == "cinematic":
        #     queue_video_generation(image.id)

    except Image.DoesNotExist:
        logger.warning(f"⚠️ Post-gen hook failed: Image ID {image_id} not found.")
    except Exception as e:
        logger.error(f"🔥 Unexpected error in post-gen hook: {e}")


def prepare_final_prompt(image):
    """
    Builds the final prompt from user input + optional style preset.
    Also returns the negative prompt.
    """
    user_prompt = (image.prompt or "").strip().strip('"')
    negative_prompt = (image.negative_prompt or "").strip()
    style = image.style

    style_prompt = ""
    style_preset = None

    if style and hasattr(style, "prompt"):
        style_prompt = (style.prompt or "").strip().strip('"')
        style_preset = getattr(style, "style_preset", "").lower()

    # Merge prompts
    if style_prompt and style_prompt not in user_prompt:
        full_prompt = f"{style_prompt}, {user_prompt}"
    else:
        full_prompt = user_prompt

    # Extract user-only (if style was embedded in front)
    if full_prompt.startswith(style_prompt):
        user_only = full_prompt[len(style_prompt) :].lstrip(", ").strip()
    else:
        user_only = user_prompt

    return full_prompt, user_only, negative_prompt, style_preset
