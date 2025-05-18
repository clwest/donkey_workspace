"""Stable Diffusion Image Generation Utility

Handles interaction with an external Stable Diffusion API to generate images from prompts.
Supports various generation options including style presets, seeds, steps, and negative prompts.
Saves image outputs locally and returns absolute URLs for frontend display.

Main Function:
- generate_stable_diffusion_image(...): Sends request to SD API, saves result, and returns image data and metadata.
"""

import requests
import uuid
from datetime import datetime
import os
import logging
from dotenv import load_dotenv
from django.conf import settings
from images.helpers.image_urls import generate_absolute_urls
from images.helpers.sanitize_file import sanitize_filename
from PIL import Image
from io import BytesIO

load_dotenv()

api_key = os.getenv("STABILITY_KEY")


logger = logging.getLogger("django")


def generate_stable_diffusion_image(
    prompt,
    width=512,
    height=512,
    api_url=None,
    api_key=None,
    style_data=None,
    negative_prompt=None,
    seed=None,
    aspect_ratio=None,
    steps=50,
):
    try:
        # Determine negative prompt: use provided override or style_data default
        if negative_prompt is None:
            neg = ""
            if hasattr(style_data, "negative_prompt") and style_data.negative_prompt:
                neg = style_data.negative_prompt
            negative_prompt_val = neg.strip()
        else:
            negative_prompt_val = str(negative_prompt).strip()
        full_prompt = prompt.strip().strip('"')

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "image/*",
        }

        files = {
            "prompt": (None, full_prompt),
            "width": (None, str(width)),
            "height": (None, str(height)),
            "output_format": (None, "webp"),
            "steps": (None, str(steps)),
        }
        if negative_prompt_val:
            files["negative_prompt"] = (None, negative_prompt_val)
        if seed is not None:
            files["seed"] = (None, str(seed))
        if aspect_ratio:
            files["aspect_ratio"] = (None, aspect_ratio)

        logger.warning("🚀 Sending request to Stable Diffusion API with payload")
        logger.warning(f"🔐 Headers: {headers}")
        logger.warning(f"📦 Files: {files}")
        logger.warning(f"🌐 URL: {api_url}")
        logger.warning(f"🎨 Using style: {style_data.name if style_data else 'None'}")

        response = requests.post(api_url, headers=headers, files=files, timeout=30)
        response.raise_for_status()

        if "image/" in response.headers.get("Content-Type", ""):
            output_dir = os.path.join(settings.MEDIA_ROOT, "generated_images")
            os.makedirs(output_dir, exist_ok=True)

            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            unique_id = str(uuid.uuid4())[:8]
            sanitized_prompt = sanitize_filename(prompt)
            file_name = f"sd_image_{sanitized_prompt}_{timestamp}_{unique_id}.webp"
            output_path = os.path.join(output_dir, file_name)

            image_data = BytesIO(response.content)
            image = Image.open(image_data)
            image.load()
            image.save(output_path, format=image.format or "WEBP")

            relative_path = os.path.join("generated_images", file_name)
            absolute_url = generate_absolute_urls([relative_path])[0]

            return {
                "status": "succeeded",
                "file_paths": [relative_path],
                "output_urls": [absolute_url],
                "used_style": style_data,
                "steps": steps,
                "engine": "stable-diffusion",
            }

        raise ValueError("Unexpected response format. Not an image.")

    except requests.exceptions.HTTPError as http_err:
        logger.error(
            f"🔥 Stability API Error Response: {response.text if 'response' in locals() else 'No response'}"
        )
        logger.error(f"🔥 HTTP error occurred: {http_err}")
    except Exception as err:
        logger.error(f"🔥 Other error occurred: {err}")

    # Return fallback if failure
    placeholder_url = settings.STATIC_URL + "fallbacks/sd_placeholder.webp"
    return {
        "status": "failed",
        "file_paths": [],
        "output_urls": [placeholder_url],
        "used_style": style_data,
        "steps": steps,
        "engine": "stable-diffusion",
    }
