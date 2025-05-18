#!/usr/bin/env python
"""
NLTK Data Loader

This module provides a centralized way to download NLTK data packages
to avoid redundant downloads across different parts of the application.
"""

import logging
import os
import nltk
import threading

logger = logging.getLogger(__name__)

# Keep track of which packages have been downloaded
_downloaded_packages = set()
_download_lock = threading.Lock()  # Thread safety for concurrent access


def ensure_nltk_data(package_name):
    """
    Ensure that an NLTK data package is downloaded, avoiding redundant downloads.

    Args:
        package_name: Name of the NLTK package to download

    Returns:
        bool: True if download successful or already downloaded
    """
    global _downloaded_packages

    # Skip if already downloaded in this session
    if package_name in _downloaded_packages:
        return True

    with _download_lock:  # Thread-safe check and download
        # Double-check after acquiring lock (another thread might have downloaded it)
        if package_name in _downloaded_packages:
            return True

        # Check if the package is already downloaded on the system
        # NLTK data is typically stored in ~/nltk_data
        try:
            nltk.data.find(
                f"{'tokenizers' if package_name == 'punkt' else 'corpora' if package_name in ['stopwords', 'words'] else ''}/{package_name}"
            )
            logger.debug(f"NLTK package '{package_name}' already exists")
            _downloaded_packages.add(package_name)
            return True
        except LookupError:
            # Package not found, need to download
            try:
                logger.info(f"Downloading NLTK package: {package_name}")
                nltk.download(package_name, quiet=True)
                _downloaded_packages.add(package_name)
                return True
            except Exception as e:
                logger.error(f"Failed to download NLTK package '{package_name}': {e}")
                return False


def load_required_nltk_data():
    """
    Load all NLTK data packages required by the application.

    Returns:
        bool: True if all packages were loaded successfully
    """
    required_packages = [
        "punkt",  # For sentence tokenization
        "stopwords",  # For removing common words
        "words",  # For word lists
    ]

    success = True
    for package in required_packages:
        if not ensure_nltk_data(package):
            success = False

    if success:
        logger.info(f"Loaded NLTK data packages: {', '.join(required_packages)}")
    else:
        logger.warning("Some NLTK data packages failed to load")

    return success
