"""
Utility functions for handling image editing workflows using Stability AI.

This module provides helper methods to:
- Construct proper API endpoints based on the edit type.
- Build multipart form payloads from a given ImageEditRequest model instance.
- Handle saving of binary image results locally after processing.

Supported edit types include erase, inpaint, outpaint, search-and-replace, and more.
"""

import os
import requests
from dotenv import load_dotenv
from django.conf import settings
from images.helpers.image_urls import generate_absolute_urls
from PIL import Image
from io import BytesIO
from datetime import datetime
import uuid
import logging

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

EDIT_ENDPOINTS = {
    "erase": "stable-image/edit/erase",
    "inpaint": "stable-image/edit/inpaint",
    "outpaint": "stable-image/edit/outpaint",
    "search_replace": "stable-image/edit/search-and-replace",
    "search_recolor": "stable-image/edit/search-and-recolor",
    "remove_background": "stable-image/edit/remove-background",
    "replace_background": "stable-image/edit/replace-background-and-relight",
    "relight": "stable-image/edit/replace-background-and-relight",
}


def get_edit_endpoint(edit_type):
    endpoint = EDIT_ENDPOINTS.get(edit_type)
    if not endpoint:
        raise NotImplementedError(f"Edit type '{edit_type}' is not supported.")
    return f"{STABILITY_BASE_URL.rstrip('/')}/{endpoint}"


def build_edit_payload(request):
    payload = {"output_format": (None, "webp")}

    files = {
        "image": open(request.input_image.path, "rb"),
    }

    if request.mask_image:
        files["mask"] = open(request.mask_image.path, "rb")

    if request.prompt:
        payload["prompt"] = (None, request.prompt)

    if request.negative_prompt:
        payload["negative_prompt"] = (None, request.negative_prompt)

    if request.edit_type == "outpaint":
        if request.left:
            payload["left"] = (None, str(request.left))
        if request.right:
            payload["right"] = (None, str(request.right))
        if request.up:
            payload["up"] = (None, str(request.up))
        if request.down:
            payload["down"] = (None, str(request.down))
        if request.creativity is not None:
            payload["creativity"] = (None, str(request.creativity))

    if request.edit_type == "search_replace":
        if request.search_prompt and request.prompt:
            payload["search_prompt"] = (None, request.search_prompt)
            payload["prompt"] = (None, request.prompt)

    if request.edit_type == "search_recolor":
        if request.select_prompt and request.prompt:
            payload["select_prompt"] = (None, request.select_prompt)
            payload["prompt"] = (None, request.prompt)

    if request.edit_type == "relight":
        payload["mode"] = (None, "async")

    if request.seed is not None:
        payload["seed"] = (None, str(request.seed))

    if request.style_preset:
        payload["style_preset"] = (None, request.style_preset)

    if request.grow_mask is not None:
        payload["grow_mask"] = (None, str(request.grow_mask))

    return payload, files


def save_edited_image(image_data, request):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    uid = str(uuid.uuid4())[:8]
    filename = f"edit_{request.edit_type}_{timestamp}_{uid}.webp"

    output_dir = os.path.join(settings.MEDIA_ROOT, "edited_images")
    os.makedirs(output_dir, exist_ok=True)

    output_path = os.path.join(output_dir, filename)
    img = Image.open(BytesIO(image_data))
    img.save(output_path, format="WEBP")

    return os.path.join("edited_images", filename)
