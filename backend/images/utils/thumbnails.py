import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from django.conf import settings
from django.core.files import File
from PIL import Image

from images.models import PromptHelper
from images.utils.stable_diffusion_api import generate_stable_diffusion_image
from images.helpers.image_urls import generate_absolute_urls

load_dotenv()
logger = logging.getLogger("django")


def create_thumbnail(original_path: str, size=(300, 300)) -> str:
    """
    Creates a resized thumbnail version of the image and returns the new file path.
    """
    try:
        img = Image.open(original_path)
        img.thumbnail(size)

        thumb_path = original_path.replace(
            ".webp", "_thumb.webp"
        )  # You can change to .jpg if needed
        img.save(thumb_path, "WEBP")

        logger.info(f"🖼️ Thumbnail created at: {thumb_path}")
        return thumb_path

    except Exception as e:
        logger.error(f"🚫 Failed to create thumbnail: {e}")
        return original_path  # fallback to original


def generate_thumbnails(image=None):
    prompt_helpers = [image.style] if image else PromptHelper.objects.all()

    for style in prompt_helpers:
        name = style.name

        if style.image_path and style.image_path.name:
            logger.info(f"🛑 Skipping thumbnail for '{name}' — already exists.")
            continue

    for style in prompt_helpers:
        prompt = style.prompt.strip()
        negative_prompt = (style.negative_prompt or "").strip()
        name = style.name

        if not prompt:
            logger.warning(f"⚠️ Skipping style '{name}' (no prompt).")
            continue

        try:
            logger.info(f"🎨 Generating thumbnail for: {name}")
            result = generate_stable_diffusion_image(
                prompt=f"{prompt}, centered, portrait view",
                width=512,
                height=512,
                api_url=f"{os.getenv('STABILITY_BASE_URL')}stable-image/generate/ultra",
                api_key=os.getenv("STABILITY_KEY"),
                steps=30,
                style_data=style,
            )

            if result.get("status") != "succeeded":
                logger.warning(f"⚠️ Thumbnail generation failed for {name}")
                continue

            image_paths = result.get("file_paths", [])
            absolute_urls = result.get("output_urls", [])

            if not image_paths:
                logger.warning(f"⚠️ No image returned for {name}")
                continue

            file_path = os.path.join(settings.MEDIA_ROOT, image_paths[0])

            if not os.path.exists(file_path):
                logger.error(f"❌ File not found: {file_path}")
                continue

            # 🔥 Create thumbnail version using Pillow
            thumbnail_path = create_thumbnail(file_path)

            with open(thumbnail_path, "rb") as f:
                style.image_path.save(
                    os.path.basename(thumbnail_path), File(f), save=True
                )

            logger.info(f"✅ Thumbnail saved to PromptHelper.image_path for {name}")
            logger.info(f"🌐 URL: {absolute_urls[0]}")

        except Exception as e:
            logger.error(f"🔥 Failed to generate thumbnail for {name}: {e}")
