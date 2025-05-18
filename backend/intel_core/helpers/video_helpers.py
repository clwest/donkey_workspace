"""
Helper functions for retrieving and processing video content.
These functions provide a reliable way to access video documents
without the type mismatches between UUID and integer IDs.
"""

import logging
from intel_core.models import Document
from typing import List, Dict, Any, Optional
from django.db.models import Q
import re
from intel_core.helpers.cache_core import get_cache, set_cache
from intel_core.helpers.document_retrieval_helpers import (
    get_documents_by_type_and_title,
    get_document_by_id,
)

# Configure logging
logger = logging.getLogger(__name__)


def get_video_documents(
    video_title: str = None, limit: int = 20
) -> List[Dict[str, Any]]:
    """
    Retrieve video documents directly from the database by title.
    This function now uses the standardized document retrieval system with caching for performance.

    Args:
        video_title: Optional title to filter by
        limit: Maximum number of documents to return

    Returns:
        List of video document dictionaries with content and metadata
    """
    try:
        # Create a cache key based on the parameters
        cache_key = f"video_docs_{video_title}_{limit}"

        # Try to get from cache first
        cached_results = get_cache(cache_key)
        if cached_results:
            logger.info(
                f"🎥 Retrieved {len(cached_results)} video documents from cache"
            )
            return cached_results

        logger.info(
            f"🎥 Attempting to retrieve video documents with title: {video_title}"
        )

        # Transform the title for broader search if needed
        broader_title = None
        if video_title:
            # Convert to lowercase for more flexible matching
            common_title = video_title.lower()
            logger.info(
                f"🎥 Added broader search for common video title: {common_title}"
            )
            broader_title = common_title

        # Use the standardized document retrieval function
        documents = get_documents_by_type_and_title(
            document_type="video", title=video_title, limit=limit
        )

        # If no results with exact title, try broader search
        if not documents and broader_title and broader_title != video_title:
            logger.info(
                f"🔍 No exact matches found, trying broader search with: {broader_title}"
            )
            documents = get_documents_by_type_and_title(
                document_type="video", title=broader_title, limit=limit
            )

        # If still no results, try with partial title matching
        if not documents and video_title:
            # Try to extract keywords from the title
            keywords = video_title.lower().split()
            for keyword in keywords:
                if len(keyword) >= 3:  # Only use keywords of sufficient length
                    logger.info(f"🔍 Trying keyword search with: {keyword}")
                    keyword_docs = get_documents_by_type_and_title(
                        document_type="video", title=keyword, limit=limit
                    )
                    if keyword_docs:
                        documents = keyword_docs
                        break

        # If still no results, try to get any video documents
        if not documents:
            logger.info("🔍 No matches found, retrieving all video documents")
            documents = get_documents_by_type_and_title(
                document_type="video", title=None, limit=limit
            )

        # Ensure we have a list of documents
        if documents and not isinstance(documents, list):
            # If a single document was returned, convert it to a list
            documents = [documents]

        # Ensure each document has a content field
        for doc in documents:
            if "document" in doc and isinstance(doc["document"], Document):
                # If the document object is present but content is missing, add it
                if "content" not in doc:
                    doc["content"] = doc["document"].content

        # Cache the results for future use (expire after 1 hour)
        if documents:
            set_cache(cache_key, documents, 3600)
            logger.info(f"🎥 Retrieved {len(documents)} video documents")
            return documents

        return []

    except Exception as e:
        logger.error(f"❌ Error retrieving video documents: {e}")
        return []


def get_video_titles() -> List[str]:
    """
    Get a list of all available video titles in the database.

    Returns:
        List of unique video titles
    """
    try:
        titles = (
            Document.objects.filter(source_type__icontains="video")
            .values_list("title", flat=True)
            .distinct()
        )

        return list(titles)
    except Exception as e:
        logger.error(f"❌ Error retrieving video titles: {e}")
        return []


def get_video_by_id(document_id) -> Optional[Dict[str, Any]]:
    """
    Retrieve a specific video document by ID.
    Now uses the standardized document retrieval system with caching.

    Args:
        document_id: The document ID

    Returns:
        Video document dictionary or None if not found
    """
    # Create a cache key
    cache_key = f"video_doc_id_{document_id}"

    # Try to get from cache first
    cached_doc = get_cache(cache_key)
    if cached_doc:
        logger.info(
            f"🎥 Retrieved video from cache: {cached_doc.get('title', 'Unknown')} (ID: {document_id})"
        )
        return cached_doc

    # Use the standardized document retrieval function
    document = get_document_by_id(document_id)

    # Check if it's a video document
    if document and (
        document.get("source_type", "").lower() == "video"
        or "video" in str(document.get("metadata", {})).lower()
    ):
        # Cache the result for future use (expire after 1 hour)
        set_cache(cache_key, document, 3600)
        return document

    return None


def is_likely_video_query(query: str) -> bool:
    """
    Determines if a query is likely requesting video content.

    Args:
        query (str): The user query string

    Returns:
        bool: True if query appears to be asking about video content
    """
    # Video-related terms
    video_terms = [
        "video",
        "watch",
        "youtube",
        "vimeo",
        "stream",
        "clip",
        "footage",
        "recording",
        "film",
        "movie",
        "tutorial",
        "screencast",
        "presentation",
        "vibe coding",
        "vibe",
    ]

    # Check for exact terms
    query_lower = query.lower()
    for term in video_terms:
        if term.lower() in query_lower:
            return True

    # Check for video title patterns
    video_patterns = [
        r"(?i)tell me about (?:the )?([\w\s\-']+?)(?:video| content)?",
        r"(?i)explain (?:the )?([\w\s\-']+?)(?:video| content)?",
        r"(?i)summarize (?:the )?([\w\s\-']+?)(?:video| content)?",
        r"(?i)what does (?:the )?([\w\s\-']+?)(?:video| content)? (?:say|show|explain)",
        r"(?i)(?:give|provide|show) me (?:information|details|insight)(?:s)? (?:on|about) ([\w\s\-']+)",
        r"(?i)(?:tell|inform) me (?:about|on) ([\w\s\-']+)",
        r"(?i)what (?:is|are) ([\w\s\-']+) about",
        r"(?i)i want to (?:learn|know) about ([\w\s\-']+)",
        r"(?i)can you (?:tell|explain to) me (?:about|what) ([\w\s\-']+)(?:is|are)?",
        r"(?i)(?:what|how|when|where|why) (?:.*?) ([\w\s\-']+)(?:\?|$|\.|,)",  # More general pattern for questions
    ]

    for pattern in video_patterns:
        if re.search(pattern, query):
            # Extract the potential video title
            match = re.search(pattern, query)
            if match and match.group(1):
                potential_title = match.group(1).lower().strip()
                # Check if the potential title matches known video titles
                known_video_titles = [
                    "vibe",
                    "vibe coding",
                    "diffusion",
                    "llm",
                    "groq",
                    "groq3",
                    "stable diffusion",
                    "how to build a startup team",
                    "startup team",
                    "groq3 prompts",
                    "prompts",
                ]
                for title in known_video_titles:
                    if (
                        title.lower() in potential_title
                        or potential_title in title.lower()
                    ):
                        return True
            else:
                # If we can't extract a title but the pattern matches, it's likely a video query
                return True

    # Check for known video titles
    known_video_titles = [
        "vibe",
        "vibe coding",
        "diffusion",
        "llm",
        "groq",
        "groq3",
        "stable diffusion",
        "how to build a startup team",
        "startup team",
        "groq3 prompts",
        "prompts",
    ]

    for title in known_video_titles:
        if title.lower() in query_lower:
            return True

    return False


def extract_video_title_from_query(query: str) -> Optional[str]:
    """
    Extract the video title from a query.

    Args:
        query (str): The user query

    Returns:
        Optional[str]: The extracted video title, or None if no title could be extracted
    """
    if not query:
        return None

    # Clean and normalize the query
    query_lower = query.lower().strip()

    # Special case for Groq3 Prompts - highest priority
    if "groq" in query_lower or "groq3" in query_lower:
        return "Groq3 Prompts"

    # Dictionary of common titles for direct lookup
    common_titles = {
        "openai demo": "OpenAI Demo",
        "claude opus": "Claude Opus",
        "vibe coding": "Vibe Coding",
        "stable diffusion": "Stable Diffusion",
    }

    # Check for direct matches in common titles
    for key, title in common_titles.items():
        if key in query_lower:
            return title

    # Patterns to extract video titles
    patterns = [
        r"(?i)tell me about (?:the )?([\w\s\-']+?)(?:video| content)?",
        r"(?i)explain (?:the )?([\w\s\-']+?)(?:video| content)?",
        r"(?i)summarize (?:the )?([\w\s\-']+?)(?:video| content)?",
        r"(?i)what does (?:the )?([\w\s\-']+?)(?:video| content)? (?:say|show|explain)",
        r"(?i)(?:give|provide|show) me (?:information|details|insight)(?:s)? (?:on|about) ([\w\s\-']+)",
        r"(?i)(?:tell|inform) me (?:about|on) ([\w\s\-']+)",
        r"(?i)what (?:is|are) ([\w\s\-']+) about",
        r"(?i)i want to (?:learn|know) about ([\w\s\-']+)",
        r"(?i)can you (?:tell|explain to) me (?:about|what) ([\w\s\-']+)(?:is|are)?",
    ]

    # Try to match patterns and extract title
    for pattern in patterns:
        match = re.search(pattern, query)
        if match and match.group(1):
            extracted_title = match.group(1).strip()

            # Check if the extracted title contains "groq"
            if "groq" in extracted_title.lower():
                return "Groq3 Prompts"

            return extracted_title

    # If no patterns match, return the original query
    return query
