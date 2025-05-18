"""
Utility for handling image upscaling requests via Stability AI.

Provides a single function `upscale_image()` that:
- Accepts an image file path, upscale type, prompt, and optional style settings.
- Sends the request to Stability AI's API with the appropriate headers and parameters.
- Returns the binary image data or raises an error if the request fails.
"""

import os
import requests
from dotenv import load_dotenv
from django.conf import settings
from images.helpers.image_urls import generate_absolute_urls
import logging
from django.conf import settings

load_dotenv()
logger = logging.getLogger("django")

STABILITY_KEY = os.getenv("STABILITY_KEY")
STABILITY_BASE_URL = os.getenv("STABILITY_BASE_URL")

HEADERS = {
    "Authorization": f"Bearer {STABILITY_KEY}",
    "Accept": "image/*",
    "stability-client-id": "donkey-betz-ai",
    "stability-client-user-id": "chris#001",
    "stability-client-version": "1.0.0",
}


def upscale_image(
    upscale_type: str,
    image_path: str,
    prompt: str,
    scale: float = 0.35,
    output_format: str = "webp",
    style_preset: str = None,
):
    try:

        upscale_url = (
            f"{STABILITY_BASE_URL.rstrip('/')}/stable-image/upscale/{upscale_type}"
        )
        # print(f"🔍 Final upscale URL: {upscale_url}")

        if not os.path.isfile(image_path):
            raise FileNotFoundError(f"File not found: {image_path}")

        with open(image_path, "rb") as img_file:
            files = {
                "image": (os.path.basename(image_path), img_file, "image/webp"),
                "prompt": (None, prompt),
                "output_format": (None, output_format),
            }

            if upscale_type == "creative":
                files["creativity"] = (None, str(scale))
                if style_preset:
                    files["style_preset"] = (None, style_preset)

            response = requests.post(upscale_url, headers=HEADERS, files=files)
            if response.status_code != 200:
                raise ValueError(f"Upscale failed: {response.text}")

            return response.content  # Binary image data

    except Exception as e:
        logger.warning(f"🔥 Error in upscaling request: {e}")
        raise
