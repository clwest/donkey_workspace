"""
Helper module to sanitize prompt strings into safe filenames.
Replaces non-alphanumeric characters with underscores and truncates to 50 characters.
"""

import re


def sanitize_filename(prompt):
    """
    Sanitize the prompt to create a safe filename.
    Removes special characters and limits length.
    """
    return re.sub(f"[^A-Za-z0-9]+", "_", prompt)[
        :50
    ]  # Replace non-alphanumeric chars and truncate
