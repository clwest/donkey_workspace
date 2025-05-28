import asyncio
from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup as Soup
import logging
from intel_core.models import Document
from typing import List, Dict, Any, Optional, Union
from django.db.models import Q
import re
from intel_core.helpers.cache_core import get_cache, set_cache
from intel_core.helpers.document_retrieval_helpers import (
    get_documents_by_type_and_title,
    get_document_by_id,
)

# Configure logging
logger = logging.getLogger(__name__)


async def async_fetch_url(url):
    """
    Fetch content from URL, including JavaScript-rendered content, using Playwright
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(url)
        content = await page.content()
        await browser.close()
        return content


def fetch_url(url):
    """
    Fetch content from a URL using Playwright.

    Args:
        url (str): The URL to fetch.

    Returns:
        str: The page content or an empty string if an error occurs.
    """
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=True
            )  # Headless mode for background processing
            user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            context = browser.new_context(user_agent=user_agent)
            page = context.new_page()

            page.goto(url, timeout=60000)  # Timeout to allow slow-loading pages
            content = page.content()  # Fetch the full page HTML

            context.close()
            browser.close()
            return content
    except Exception as e:
        print(f"Error in fetch_url: {e}")
        return ""


def fetch_webpage_metadata(url):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Debug: Print URL before navigation
        print(f"Navigating to URL: {url}")

        if not isinstance(url, str):
            raise ValueError(f"Expected URL to be a string, but got {type(url)}: {url}")

        page.goto(url)
        title = page.title()  # Extracts the page title
        browser.close()
        return title


def extract_visible_text(html_content):
    """Return cleaned visible text using a richer extraction strategy."""

    soup = Soup(html_content, "html.parser")

    # Strip undesirable elements
    for tag in soup([
        "script",
        "style",
        "meta",
        "link",
        "noscript",
        "iframe",
        "header",
        "footer",
        "nav",
        "aside",
    ]):
        tag.decompose()

    # Prefer <article> or <main> content if available
    container = soup.find("article") or soup.find("main")
    if container:
        text = container.get_text(separator=" ", strip=True)
    else:
        text = soup.get_text(separator=" ", strip=True)

    return " ".join(text.split())


def get_documents(
    document_type: str = None,
    title: str = None,
    content_query: str = None,
    limit: int = 5,
) -> List[Dict[str, Any]]:
    """
    Retrieve documents from the database with type and title filtering.
    This function uses the standardized document retrieval system with caching.

    Args:
        document_type: Optional document type to filter by (e.g., 'pdf', 'url')
        title: Optional title to filter by
        content_query: Optional query to search in document content
        limit: Maximum number of documents to return

    Returns:
        List of document dictionaries with content and metadata
    """
    # Create a cache key based on the parameters
    cache_key = f"docs_{document_type}_{title}_{content_query}_{limit}"

    # Try to get from cache first
    cached_results = get_cache(cache_key)
    if cached_results:
        logger.info(f"📄 Retrieved {len(cached_results)} documents from cache")
        return cached_results

    logger.info(f"📄 Retrieving documents with type: {document_type}, title: {title}")

    # Use the standardized document retrieval function
    documents = get_documents_by_type_and_title(
        document_type=document_type,
        title=title,
        content_query=content_query,
        limit=limit,
    )

    # Cache the results for future use (expire after 1 hour)
    if documents:
        set_cache(cache_key, documents, 3600)

    return documents


def get_document_by_content(
    query: str, document_type: str = None, limit: int = 5
) -> List[Dict[str, Any]]:
    """
    Search for documents based on their content.

    Args:
        query: Text to search for in document content
        document_type: Optional document type to filter by
        limit: Maximum number of documents to return

    Returns:
        List of document dictionaries with matching content
    """
    return get_documents(document_type=document_type, content_query=query, limit=limit)


def is_document_query(query: str) -> bool:
    """
    Detect if a query is likely asking about a document.

    Args:
        query: The user query to check

    Returns:
        Boolean indicating if this is likely a document query
    """
    # List of document-related terms
    document_terms = [
        "document",
        "pdf",
        "file",
        "article",
        "paper",
        "publication",
        "report",
        "book",
        "text",
        "read",
        "attachment",
        "content",
    ]

    query_lower = query.lower()

    # Check for explicit document mentions
    for term in document_terms:
        if term in query_lower:
            logger.info(f"✅ Detected document query with term: {term}")
            return True

    # Check for patterns like "in the X document", "about X document", etc.
    document_patterns = [
        r"about\s+the\s+([^\s]+(?:\s+[^\s]+){0,3})\s+(?:document|pdf|article|paper|report)",
        r"in\s+the\s+([^\s]+(?:\s+[^\s]+){0,3})\s+(?:document|pdf|article|paper|report)",
        r"from\s+the\s+([^\s]+(?:\s+[^\s]+){0,3})\s+(?:document|pdf|article|paper|report)",
    ]

    for pattern in document_patterns:
        if re.search(pattern, query_lower):
            logger.info(f"✅ Detected document query with pattern: {pattern}")
            return True

    return False


def extract_topic_from_query(query: str) -> Optional[str]:
    """
    Extract potential document topic or title from a query.

    Args:
        query: The user query to extract from

    Returns:
        Extracted topic/title or None if not found
    """
    # Patterns for extracting document topics
    patterns = [
        r"about\s+the\s+([^\s]+(?:\s+[^\s]+){0,5})\s+(?:document|pdf|article|paper|report)",
        r"information\s+(?:on|about)\s+([^\s]+(?:\s+[^\s]+){0,5})",
        r"tell\s+me\s+about\s+([^\s]+(?:\s+[^\s]+){0,5})",
        r"what\s+(?:is|are)\s+([^\s]+(?:\s+[^\s]+){0,5})",
        r"explain\s+([^\s]+(?:\s+[^\s]+){0,5})",
        r"summarize\s+([^\s]+(?:\s+[^\s]+){0,5})",
    ]

    # Try to extract topic using patterns
    for pattern in patterns:
        match = re.search(pattern, query.lower())
        if match:
            topic = match.group(1)
            if len(topic) > 3:  # Only consider topics with reasonable length
                logger.info(f"✅ Extracted topic: {topic}")
                return topic

    # Fallback: if query is short, treat entire query as topic
    if len(query.split()) <= 5:
        logger.info(f"✅ Using entire query as topic: {query}")
        return query

    return None


def process_document_query(query: str) -> Dict[str, Any]:
    """
    Process a query about documents and retrieve relevant document context.
    This ensures all document types are handled consistently.

    Args:
        query: User's document-related query

    Returns:
        Dictionary with relevant document context and metadata
    """
    # Initialize result
    result = {
        "is_document_query": False,
        "extracted_topic": None,
        "documents": [],
        "document_type": None,
    }

    # Check if it's a document query
    result["is_document_query"] = is_document_query(query)
    if not result["is_document_query"]:
        return result

    # Extract topic
    result["extracted_topic"] = extract_topic_from_query(query)
    if not result["extracted_topic"]:
        return result

    # Determine document type if explicitly mentioned
    document_types = {
        "pdf": ["pdf", "document", "paper", "report"],
        "url": ["url", "website", "webpage", "web page", "article", "link"],
        "video": ["video", "youtube", "clip", "recording"],
    }

    query_lower = query.lower()
    for doc_type, keywords in document_types.items():
        if any(keyword in query_lower for keyword in keywords):
            result["document_type"] = doc_type
            break

    # Retrieve documents
    documents = get_documents(
        document_type=result["document_type"], title=result["extracted_topic"], limit=5
    )

    # If no direct matches, try content search
    if not documents:
        documents = get_document_by_content(
            query=result["extracted_topic"],
            document_type=result["document_type"],
            limit=5,
        )

    result["documents"] = documents

    return result


def get_document_memory_status(document: Document) -> dict:
    """Return memory stats for a document used by assistants."""
    from intel_core.models import DocumentChunk
    from memory.models import MemoryEntry

    total_chunks = DocumentChunk.objects.filter(document=document).count()
    embedded_chunks = DocumentChunk.objects.filter(
        document=document, embedding__isnull=False
    ).count()
    coverage = round((embedded_chunks / total_chunks) * 100, 1) if total_chunks else 0.0

    tags = list(document.tags.values_list("name", flat=True))

    last_entry = (
        MemoryEntry.objects.filter(document=document).order_by("-created_at").first()
    )
    last_summary = ""
    if last_entry:
        last_summary = last_entry.summary or (last_entry.event[:80] if last_entry.event else "")

    return {
        "document_id": str(document.id),
        "title": document.title,
        "slug": document.slug,
        "total_chunks": total_chunks,
        "embedded_chunks": embedded_chunks,
        "embedding_coverage": coverage,
        "tags": tags,
        "last_chunk_summary": last_summary,
        "linked_at": document.created_at.isoformat().replace("+00:00", "Z"),
    }
