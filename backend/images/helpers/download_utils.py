"""
Helper functions for downloading images from external URLs and validating their structure.
Includes functionality to stream and save remote images locally.
"""

import requests
from urllib.parse import urlparse


def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def download_image(image_url, output_file):
    """
    Downloads an image from a URL and saves it to the specified filename.
    """
    if not is_valid_url(image_url):
        raise ValueError(f"Invalid URL: {image_url}")
    try:
        response = requests.get(image_url, stream=True)
        response.raise_for_status()
        with open(output_file, "wb") as output_file:
            for chunk in response.iter_content(1024):
                output_file.write(chunk)
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image: {e} ")
        return False
