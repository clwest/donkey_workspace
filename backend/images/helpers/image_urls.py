"""
Helper utilities for converting relative image paths into fully-qualified media URLs using the Django settings.
This is typically used to turn file paths from MEDIA_ROOT into accessible URLs via MEDIA_URL and BASE_URL.
"""

import os
from dotenv import load_dotenv
from django.conf import settings

load_dotenv()


def generate_absolute_urls(image_paths):
    """
    Converts relative media paths into absolute URLs, unless already absolute.

    Args:
        image_paths (list or str): Relative paths like 'generated_images/...'

    Returns:
        list: List of absolute URLs like 'http://localhost:8000/media/generated_images/...'
    """
    base_url = getattr(settings, "BASE_URL", "http://localhost:8000")
    media_prefix = settings.MEDIA_URL or "/media/"

    if isinstance(image_paths, str):
        image_paths = [image_paths]

    print(f"Base URL: {base_url}")
    print(f"Image paths: {image_paths}")

    try:
        absolute_urls = []
        for path in image_paths:
            if path.startswith("http://") or path.startswith("https://"):
                absolute_urls.append(path)
            else:
                clean_path = path.lstrip("/")
                absolute_url = f"{base_url.rstrip('/')}{media_prefix}{clean_path}"
                absolute_urls.append(absolute_url)

        print(f"Generated absolute URLs: {absolute_urls}")
        return absolute_urls
    except Exception as e:
        print(f"Error in generate_absolute_urls: {e}")
        raise
