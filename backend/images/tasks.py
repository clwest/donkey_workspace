import os
import logging
import requests
from django.conf import settings
from django.utils.timezone import now
from openai import OpenAI
from celery import shared_task
from dotenv import load_dotenv
import uuid
from django.forms.models import model_to_dict
from PIL import Image
from images.helpers.post_generation_hooks import trigger_post_generation_hook
from io import BytesIO
from urllib.parse import urlparse
from datetime import datetime
from .models import Image, Edit, UpscaleImage
from images.helpers.download_utils import download_image
from images.helpers.image_urls import generate_absolute_urls
from images.helpers.sanitize_file import sanitize_filename
from images.utils.stable_diffusion_api import generate_stable_diffusion_image
from images.utils.editing import (
    get_edit_endpoint,
    build_edit_payload,
    save_edited_image,
    HEADERS,
)
from images.models import PromptHelper
import re
from tts.tasks import queue_tts_story


load_dotenv()

logger = logging.getLogger("django")

stability_url = os.getenv("STABILITY_BASE_URL")
stability_api = os.getenv("STABILITY_KEY")
STABILITY_API_KEY = os.getenv("STABILITY_KEY")
STABILITY_BASE_URL = os.getenv("STABILITY_BASE_URL")
openai_api = os.getenv("OPENAI_API")
client = OpenAI()


# Supported values from Stability API docs
VALID_STYLE_PRESETS = {
    "enhance",
    "anime",
    "photographic",
    "digital-art",
    "comic-book",
    "fantasy-art",
    "line-art",
    "analog-film",
    "neon-punk",
    "isometric",
    "low-poly",
    "origami",
    "modeling-compound",
    "cinematic",
    "3d-model",
    "pixel-art",
    "tile-texture",
}

EDIT_ENDPOINTS = {
    "remove_background": "v2beta/stable-image/edit/remove-background",
    "inpaint": "v2beta/stable-image/edit/inpaint",
    "outpaint": "v2beta/stable-image/edit/outpaint",
    "search_replace": "v2beta/stable-image/edit/search-and-replace",
    "search_recolor": "v2beta/stable-image/edit/search-and-recolor",
    "erase": "v2beta/stable-image/edit/erase",
    "relight": "v2beta/stable-image/edit/relight",
}


def merge_style_and_user_prompt(style_prompt, user_prompt):
    """
    Ensures that user prompt is always included and not duplicated,
    and that style and user prompts are clearly merged.
    """
    style_prompt = style_prompt.strip().strip('"')
    user_prompt = user_prompt.strip().strip('"')

    if not style_prompt:
        return user_prompt

    if style_prompt in user_prompt:
        return user_prompt  # already included

    return f"{style_prompt}, {user_prompt}"


def strip_style_prompt(prompt, style_prompt):
    if not style_prompt:
        return prompt.strip()
    # Remove style_prompt from the beginning if it's there
    if prompt.startswith(style_prompt):
        return prompt[len(style_prompt) :].lstrip(", ").strip()
    return prompt.strip()


@shared_task
def debug_sd_env():
    return {
        "STABILITY_URL": os.getenv("STABILITY_BASE_URL"),
        "STABILITY_API_KEY": os.getenv("STABILITY_KEY"),
    }


@shared_task
def process_sd_image_request(request_id):
    try:
        request = Image.objects.filter(id=request_id).first()
        if not request:
            logger.error(f"❌ Image request {request_id} not found.")
            return

        request.status = "processing"
        request.save()
        # 🧠 Route based on model_backend (stability vs replicate)
        logger.info(
            f"🧠 Routing image {request.id} to backend: {request.model_backend}"
        )
        if request.model_backend == "replicate":
            try:
                from trainers.helpers.replicate_helpers import generate_image

                prediction = generate_image(request.prompt, require_trigger_word=False)
                request.status = "queued"
                request.prediction_id = prediction.id
                request.save()
            except Exception as e:
                request.status = "failed"
                request.error_message = str(e)
                request.save()
            return

        # 🧠 Final prompt + negative + preset via hook
        from images.helpers.prompt_generation_hook import prepare_final_prompt

        full_prompt, user_prompt_only, negative_prompt = prepare_final_prompt(request)

        # 🚀 Log generation details
        logger.warning(f"🧪 Final SD Prompt: {full_prompt}")
        logger.warning(f"📓 User-only: {user_prompt_only}")
        logger.warning(f"❌ Negative Prompt: {negative_prompt}")

        # 🎨 Generate the image
        sd_result = generate_stable_diffusion_image(
            prompt=full_prompt,
            width=request.width,
            height=request.height,
            api_url=f"{STABILITY_BASE_URL}stable-image/generate/ultra",
            api_key=STABILITY_API_KEY,
            style_data=request.style,
            negative_prompt=negative_prompt,
            steps=request.steps,
        )

        if sd_result.get("status") != "succeeded":
            raise ValueError("Stable Diffusion generation failed.")

        image_paths = sd_result.get("file_paths") or []
        absolute_urls = generate_absolute_urls(image_paths)

        if not image_paths or not absolute_urls:
            raise ValueError("No images returned from generation.")

        # 💾 Save image
        rel_path = image_paths[0]
        abs_url = absolute_urls[0]

        request.file_path = rel_path
        request.output_url = abs_url
        request.output_urls = absolute_urls
        request.status = "completed"
        request.completed_at = now()

        request.save()

        # 🧙 Trigger post-generation hook
        trigger_post_generation_hook(request.id)

        logger.info(f"✅ SD image complete for request {request.id}")
        logger.info(f"🌐 Output URL: {abs_url}")

    except Exception as e:
        logger.error(f"🔥 Error in SD processing: {e}")
        if request:
            request.status = "failed"
            request.output_urls = []
            request.save()

    finally:
        if request:
            request.updated_at = now()
            request.save()


@shared_task
def process_upscale_image_request(payload):
    import logging
    import os
    from django.conf import settings
    from django.contrib.auth import get_user_model
    from images.utils.upscaling import upscale_image
    from images.models import Image, UpscaleImage
    from images.helpers.image_urls import generate_absolute_urls

    logger = logging.getLogger("django")

    try:
        request_id = payload.get("request_id")
        user_id = payload.get("user_id")
        upscale_type = payload.get("upscale_type", "conservative").lower()
        scale = float(payload.get("scale", 0.35))
        negative_prompt = payload.get("negative_prompt")
        prompt = payload.get("prompt", "Highly detailed realistic upscale")

        # Get image and user
        image = Image.objects.get(id=request_id)
        User = get_user_model()
        user = User.objects.get(id=user_id)

        image.status = "processing"
        image.save()

        # Try to get a usable URL
        output_url = image.output_url or (
            image.output_urls[0] if image.output_urls else None
        )

        if not output_url:
            logger.warning(f"❌ No usable output URL found for image {image.id}")
            image.status = "failed"
            image.save()
            return

        # Local path resolution
        base_path = output_url.replace("http://localhost:8000/media/", "")
        original_path = os.path.join(settings.MEDIA_ROOT, base_path)

        if not os.path.exists(original_path):
            raise FileNotFoundError(
                f"Original image not found locally: {original_path}"
            )

        logger.info(f"📤 Sending image to Stability.ai upscaler: {original_path}")

        upscaled_data = upscale_image(
            upscale_type=upscale_type,
            image_path=original_path,
            prompt=prompt,
            scale=scale,
        )

        # Save upscaled file
        output_filename = f"upscaled_{upscale_type}_{os.path.basename(original_path)}"
        output_dir = os.path.join(settings.MEDIA_ROOT, "upscaled_images")
        os.makedirs(output_dir, exist_ok=True)

        output_path = os.path.join(output_dir, output_filename)
        with open(output_path, "wb") as f:
            f.write(upscaled_data)

        relative_path = os.path.join("upscaled_images", output_filename)
        absolute_url = generate_absolute_urls([relative_path])[0]

        # Save to DB
        UpscaleImage.objects.create(
            request=image,
            user=user,
            upscale_type=upscale_type,
            output_url=absolute_url,
        )

        image.status = "succeeded"
        image.save()

        logger.info(f"✅ Upscaling succeeded for image {request_id}")
        logger.info(f"🖼️ Output URL: {absolute_url}")

    except Exception as e:
        logger.warning(f"🔥 Error in upscaling task: {e}")
        try:
            image.status = "failed"
            image.output_urls = []
            image.save()
        except:
            pass


@shared_task
def process_edit_image_request(payload):
    import logging
    from django.conf import settings
    from django.contrib.auth import get_user_model
    from images.utils.editing import (
        get_edit_endpoint,
        build_edit_payload,
        save_edited_image,
    )
    from images.models import Edit, Image

    logger = logging.getLogger("django")

    try:
        edit_id = payload.get("edit_id")
        user_id = payload.get("user_id")

        User = get_user_model()
        user = User.objects.get(id=user_id)
        edit_request = Edit.objects.get(id=edit_id)

        endpoint = get_edit_endpoint(edit_request.edit_type)
        data, files = build_edit_payload(edit_request)

        logger.warning(f"🚀 Editing image: {endpoint}")
        response = requests.post(
            endpoint, headers=settings.HEADERS, files=files, data=data
        )

        if response.status_code != 200:
            raise Exception(f"Edit failed: {response.text}")

        relative_path = save_edited_image(response.content, edit_request)
        absolute_url = generate_absolute_urls([relative_path])[0]

        edit_request.output_url = absolute_url
        edit_request.save()

        logger.info(f"✅ Edit succeeded for image {edit_id}")
        logger.info(f"🖼️ Edited URL: {absolute_url}")

    except Exception as e:
        logger.warning(f"🔥 Error editing image: {e}")
