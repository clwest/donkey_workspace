"""
Document retrieval helper functions for unified handling of all document types.

This module provides standardized functions for retrieving documents from the database,
regardless of their type (video, pdf, url, etc). It ensures consistent handling and
response formatting across all document types.
"""

import logging
import re
from typing import List, Dict, Any, Optional, Union
from django.db.models import Q
from intel_core.models import Document
from intel_core.helpers.cache_core import get_cache, set_cache

# Configure logging
logger = logging.getLogger(__name__)


def get_documents_by_type_and_title(
    document_type: Optional[str] = None,
    title: Optional[str] = None,
    content_query: Optional[str] = None,
    limit: int = 5,
) -> List[Dict[str, Any]]:
    """
    Retrieve documents from the database with type and title filtering.

    This function provides a standardized way to retrieve documents regardless of type,
    ensuring consistent handling for videos, PDFs, URLs, and other document types.

    Args:
        document_type: Optional document type to filter by (e.g., 'video', 'pdf', 'url')
        title: Optional title to filter by
        content_query: Optional query to search in document content
        limit: Maximum number of documents to return

    Returns:
        List of document dictionaries with content and metadata
    """
    try:
        # Create a cache key based on the parameters
        cache_key = f"docs_{document_type}_{title}_{content_query}_{limit}"

        # Try to get from cache first
        cached_results = get_cache(cache_key)
        if cached_results:
            logger.info(f"📚 Retrieved {len(cached_results)} documents from cache")
            return cached_results

        # Start with base query
        doc_query = Document.objects.all()

        # Apply filters if provided
        if document_type:
            doc_query = doc_query.filter(source_type__iexact=document_type)

        if title:
            # For title, use a more flexible search
            title_query = Q(title__icontains=title)

            # Also check metadata for title
            metadata_title_query = Q(metadata__title__icontains=title)

            # Combine with OR
            doc_query = doc_query.filter(title_query | metadata_title_query)

        if content_query:
            # For content, also use a flexible search
            doc_query = doc_query.filter(content__icontains=content_query)

        # Get the documents
        documents = list(doc_query.order_by("-created_at")[:limit])

        # Convert to dictionaries with consistent format
        result = []
        for doc in documents:
            # Create a standardized document dictionary
            doc_dict = {
                "id": doc.id,
                "title": doc.title,
                "content": doc.content,
                "source_type": doc.source_type,
                "metadata": doc.metadata,
                "created_at": doc.created_at.isoformat(),
                "document": doc,  # Include the actual document object for reference
                "similarity": (
                    0.95 if title and title.lower() in doc.title.lower() else 0.85
                ),  # Default similarity
                "text": (
                    doc.content[:500] + "..." if len(doc.content) > 500 else doc.content
                ),  # Preview text
            }
            result.append(doc_dict)

        # Cache the results for future use (expire after 1 hour)
        set_cache(cache_key, result, 3600)

        return result
    except Exception as e:
        logger.error(f"❌ Error retrieving documents: {e}")
        return []


def get_document_by_id(document_id: Union[str, int]) -> Optional[Dict[str, Any]]:
    """
    Retrieve a specific document by ID.

    Args:
        document_id: The document ID

    Returns:
        Document dictionary or None if not found
    """
    try:
        # Create a cache key
        cache_key = f"doc_id_{document_id}"

        # Try to get from cache first
        cached_doc = get_cache(cache_key)
        if cached_doc:
            logger.info(
                f"📄 Retrieved document from cache: {cached_doc.get('title', 'Unknown')} (ID: {document_id})"
            )
            return cached_doc

        # Handle both string and integer IDs
        if isinstance(document_id, str):
            try:
                document_id = int(document_id)
            except (ValueError, TypeError):
                # If can't convert to int, keep as is (might be UUID)
                pass

        document = Document.objects.filter(id=document_id).first()

        if not document:
            logger.warning(f"⚠️ Document with ID {document_id} not found")
            return None

        # Clean and process content for better quality
        processed_content = process_document_content(
            document.content, document.source_type
        )

        doc_dict = {
            "id": document.id,
            "title": document.title,
            "content": processed_content,
            "source_type": document.source_type,
            "metadata": document.metadata or {},
            "created_at": (
                document.created_at.isoformat() if document.created_at else None
            ),
        }

        # Cache the result for future use (expire after 1 hour)
        set_cache(cache_key, doc_dict, 3600)

        logger.info(f"✅ Retrieved document: {document.title} (ID: {document.id})")
        return doc_dict

    except Exception as e:
        logger.error(f"❌ Error retrieving document by ID: {str(e)}")
        return None


def process_document_content(content: str, source_type: str) -> str:
    """
    Process document content to improve quality and usefulness.
    This helps with the "not enough valid text" warning by ensuring content is clean and useful.

    Args:
        content: The raw document content
        source_type: The type of document (video, pdf, url, etc.)

    Returns:
        Processed content that is clean and useful
    """
    if not content:
        return ""

    # Ensure we're working with a string
    if not isinstance(content, str):
        content = str(content)

    # Remove excessive whitespace
    content = re.sub(r"\s+", " ", content).strip()

    # Handle short content by providing more context based on type
    if len(content) < 100:
        logger.warning(f"⚠️ Document content is very short ({len(content)} chars)")
        if source_type.lower() == "video":
            content += " [Note: This video content may be limited. The transcript may not fully capture all discussions in the video.]"
        elif source_type.lower() == "pdf":
            content += " [Note: This PDF content may be limited. There might be more information in the original document including charts or images.]"
        elif source_type.lower() in ["url", "web"]:
            content += " [Note: This webpage content may be limited. The content may include other elements like images or interactive features.]"

    # Limit to a reasonable size while keeping enough context
    if len(content) > 3000:
        # Take first and last parts to preserve context
        first_part = content[:2000].strip()
        last_part = content[-1000:].strip()
        content = f"{first_part}\n...\n{last_part}"

    return content


def get_document_by_content_quality(
    query: str,
    document_type: Optional[str] = None,
    min_length: int = 200,
    limit: int = 5,
) -> List[Dict[str, Any]]:
    """
    Retrieve documents with a focus on content quality. This function specifically
    addresses the "not enough valid text" warning by prioritizing documents with
    substantial content.

    Args:
        query: Query to search for
        document_type: Optional document type to filter by
        min_length: Minimum content length to consider
        limit: Maximum number of documents to return

    Returns:
        List of high-quality document dictionaries
    """
    try:
        # Get documents using the standard function
        all_docs = get_documents_by_type_and_title(
            document_type=document_type,
            title=query,
            limit=limit * 2,  # Get more to filter
        )

        if not all_docs:
            return []

        # Filter for quality documents
        quality_docs = []
        for doc in all_docs:
            content = doc.get("content", "")
            # Check content length and quality indicators
            if len(content) >= min_length and not content.isspace():
                quality_docs.append(doc)

        # Add logs about quality filtering
        logger.info(
            f"📊 Content quality filtering: {len(quality_docs)}/{len(all_docs)} documents passed quality check"
        )

        # If we still don't have enough quality docs, use the best of what we have
        if not quality_docs and all_docs:
            # Sort by content length as a basic quality metric
            sorted_docs = sorted(
                all_docs, key=lambda d: len(d.get("content", "")), reverse=True
            )
            quality_docs = sorted_docs[:limit]
            logger.info(
                f"⚠️ No documents passed quality filter, using top {len(quality_docs)} by length"
            )

        return quality_docs[:limit]

    except Exception as e:
        logger.error(f"❌ Error retrieving quality documents: {str(e)}")
        return []


def is_document_query(query: str) -> bool:
    """
    Detect if a query is likely asking about any type of document.
    This function provides a unified way to detect document queries regardless of type.

    Args:
        query: The user query to check

    Returns:
        Boolean indicating if this is likely a document query
    """
    # List of document-related terms for any document type
    document_terms = [
        "document",
        "pdf",
        "file",
        "article",
        "paper",
        "publication",
        "page",
        "report",
        "book",
        "text",
        "read",
        "content",
        "video",
        "watch",
        "clip",
        "recording",
        "transcript",
        "webpage",
        "website",
        "site",
        "url",
    ]

    query_lower = query.lower()

    # Check for explicit document mentions
    for term in document_terms:
        if term in query_lower:
            return True

    # Check for patterns like "tell me about X", "summarize X", etc.
    document_patterns = [
        r"tell\s+(?:me\s+)?about\s+(?:the\s+)?([^\s]+(?:\s+[^\s]+){0,3})",
        r"summarize\s+(?:the\s+)?([^\s]+(?:\s+[^\s]+){0,3})",
        r"(?:what|explain|describe)\s+(?:is|are|does)\s+(?:the\s+)?([^\s]+(?:\s+[^\s]+){0,3})",
    ]

    for pattern in document_patterns:
        if re.search(pattern, query_lower):
            return True

    return False


def enhanced_document_context(documents, query, max_content_per_doc=500):
    """
    Build an enhanced, well-structured context from retrieved documents for better RAG responses.

    This function creates a formatted context string that:
    1. Preserves document structure and semantic relationships
    2. Includes proper citations and references
    3. Structures information in a way that encourages better AI synthesis

    Args:
        documents (List[Dict]): Retrieved documents with content and metadata
        query (str): The original user query for context
        max_content_per_doc (int): Maximum characters to include per document

    Returns:
        str: Formatted context string for high-quality RAG responses
    """
    if not documents:
        return "No relevant information found."

    # Start with a clear header that sets expectations
    context_parts = [
        "I'll answer based on the following sources:",
    ]

    # Add document reference list for citations
    for i, doc in enumerate(documents, 1):
        title = doc.get("title", "") or doc.get("document", {}).get("title", "Untitled")
        source_type = doc.get("source_type", "") or doc.get("document", {}).get(
            "source_type", "Document"
        )
        content_id = doc.get("content_id", "") or doc.get("document", {}).get("id", "")

        # Format nicely with brackets for citation numbers
        ref_line = f"[{i}] {title} ({source_type})"
        if "created_at" in doc:
            created_date = (
                doc.get("created_at", "").split("T")[0]
                if isinstance(doc.get("created_at", ""), str)
                else ""
            )
            if created_date:
                ref_line += f", {created_date}"

        context_parts.append(ref_line)

    # Group documents by type for better organization
    doc_groups = {}
    for i, doc in enumerate(documents, 1):
        source_type = doc.get("source_type", "") or doc.get("document", {}).get(
            "source_type", "Document"
        )
        if source_type.lower() not in doc_groups:
            doc_groups[source_type.lower()] = []

        # Add document with its citation number
        doc_groups[source_type.lower()].append((i, doc))

    # Add a separator
    context_parts.append("\n---\n")

    # For each document group, add relevant content
    for source_type, docs in doc_groups.items():
        # Format header based on source type
        if "technical" in source_type or "academic" in source_type:
            group_header = "Technical Documentation:"
        elif "video" in source_type:
            group_header = "Video Content:"
        elif "web" in source_type or "url" in source_type:
            group_header = "Web Content:"
        elif "news" in source_type:
            group_header = "News Articles:"
        else:
            group_header = f"{source_type.title()} Content:"

        context_parts.append(group_header)

        # Add content from each document in this group
        for citation_num, doc in docs:
            # Get content and title
            content = (
                doc.get("content", "")
                or doc.get("text", "")
                or doc.get("document", {}).get("content", "No content available")
            )
            title = doc.get("title", "") or doc.get("document", {}).get(
                "title", "Untitled"
            )

            # Format with citation number
            doc_header = f"From [{citation_num}] {title}:"
            context_parts.append(doc_header)

            # If content is too long, extract the most relevant segments
            if len(content) > max_content_per_doc:
                # Determine key segments (this could be enhanced with NLP)
                segments = _extract_relevant_segments(
                    content, query, max_content_per_doc
                )

                # Add extracted segments
                for segment in segments:
                    context_parts.append(segment)

                # Indicate truncation
                context_parts.append(
                    f"[Additional content from [{citation_num}] truncated for brevity]"
                )
            else:
                # Content is manageable, include it all
                context_parts.append(content)

        # Add separator between document groups
        context_parts.append("---")

    # Add instructions for the response
    instructions = [
        "\nWhen responding:",
        "- Synthesize information across sources when relevant",
        "- Use citation numbers [1], [2], etc. when referencing specific information",
        "- Format your response using Markdown with headings, bullet points, and bold for key points",
        "- If the information doesn't fully answer the query, acknowledge limitations",
        "- Be concise but informative",
        "- Organize information logically",
    ]
    context_parts.append("\n".join(instructions))

    return "\n\n".join(context_parts)


def _extract_relevant_segments(content, query, max_chars):
    """
    Extract the most relevant segments from content based on query relevance.

    Args:
        content (str): Document content to extract from
        query (str): Query to determine relevance
        max_chars (int): Maximum total characters to extract

    Returns:
        List[str]: Extracted document segments
    """
    # Split content into paragraphs
    paragraphs = [p.strip() for p in content.split("\n\n") if p.strip()]
    if not paragraphs:
        paragraphs = [p.strip() for p in content.split("\n") if p.strip()]

    # If few paragraphs, return all within max_chars
    if sum(len(p) for p in paragraphs) <= max_chars:
        return paragraphs

    # Split into sentences for finer granularity
    import re

    all_sentences = []
    for paragraph in paragraphs:
        # Split by common sentence terminators while preserving them
        sentences = re.split(r"(?<=[.!?])\s+", paragraph)
        sentences = [s.strip() for s in sentences if s.strip()]
        all_sentences.extend(sentences)

    # Score paragraphs and sentences by relevance to query
    query_terms = set(query.lower().split())

    # Identify if this is a library-related query
    is_library_query = any(
        term in query.lower()
        for term in [
            "library",
            "libraries",
            "package",
            "packages",
            "module",
            "modules",
            "import",
            "dependency",
            "dependencies",
        ]
    )

    # Identify if this is an installation query
    is_installation_query = any(
        term in query.lower()
        for term in ["install", "installation", "setup", "configure", "configuration"]
    )

    # Score sentences
    scored_sentences = []
    for sentence in all_sentences:
        # Simple relevance scoring
        score = 0
        sentence_lower = sentence.lower()

        for term in query_terms:
            if len(term) > 3:  # Ignore short terms
                term_count = sentence_lower.count(term)
                score += term_count * 2  # Double the weight of exact matches

                # Check for partial matches (e.g., "install" matches "installation")
                if term_count == 0 and len(term) > 4:
                    for word in sentence_lower.split():
                        if term in word or word in term:
                            score += 1

        # Special handling for library-related queries
        if is_library_query:
            # Boost sentences containing library-related terms
            if any(
                term in sentence_lower
                for term in [
                    "library",
                    "package",
                    "module",
                    "import",
                    "pip",
                    "npm",
                    "dependency",
                ]
            ):
                score += 5
            # Boost sentences containing code patterns
            if (
                "```" in sentence
                or "import " in sentence
                or "require(" in sentence
                or "from " in sentence
            ):
                score += 3

        # Special handling for installation queries
        if is_installation_query:
            # Boost sentences containing installation instructions
            if any(
                term in sentence_lower
                for term in [
                    "install",
                    "pip install",
                    "npm install",
                    "setup",
                    "configure",
                ]
            ):
                score += 5
            # Boost sentences containing command line examples
            if (
                "$" in sentence
                or ">" in sentence
                or "pip" in sentence
                or "npm" in sentence
            ):
                score += 3

        # Boost score for sentences with structure indicators
        if re.search(r"^#+\s+", sentence):  # Heading
            score += 5
        if re.search(r"^[-*•]\s+", sentence, re.MULTILINE):  # List
            score += 3
        if re.search(
            r"\b(important|key|summary|conclusion)\b", sentence_lower
        ):  # Key indicators
            score += 2

        scored_sentences.append((sentence, score))

    # Sort by relevance score
    scored_sentences.sort(key=lambda x: x[1], reverse=True)

    # Return top sentences up to max_chars
    result = []
    total_chars = 0

    # Always include the highest scored sentence even if it's long
    if scored_sentences:
        top_sentence, _ = scored_sentences[0]
        result.append(top_sentence)
        total_chars += len(top_sentence)
        scored_sentences.pop(0)

    # Add the most relevant sentences until we approach max_chars
    for sentence, score in scored_sentences:
        if total_chars + len(sentence) <= max_chars:
            result.append(sentence)
            total_chars += len(sentence)
        else:
            # If we're approaching max_chars, stop adding more sentences
            break

    # Group adjacent sentences from the same paragraph for better context
    # This is a post-processing step that preserves the max_chars limit
    final_result = []
    current_segment = []

    for sentence in result:
        if current_segment and total_chars <= max_chars:
            # If current segment + new sentence is still under max_chars, add to current segment
            combined = " ".join(current_segment + [sentence])
            if len(combined) <= max_chars:
                current_segment.append(sentence)
            else:
                # If adding would exceed max_chars, finish current segment and start a new one
                final_result.append(" ".join(current_segment))
                current_segment = [sentence]
        else:
            current_segment.append(sentence)

    # Add the last segment if it exists
    if current_segment:
        final_result.append(" ".join(current_segment))

    # Final check to ensure we're within max_chars
    while final_result and sum(len(segment) for segment in final_result) > max_chars:
        # Remove the least important segment (last one) until we're under the limit
        final_result.pop()

    return final_result


def format_retrieved_content(retrieved_content, query=None):
    """
    Format retrieved content into a structured response with proper citations.

    Args:
        retrieved_content (dict): Content retrieved from search
        query (str, optional): Original user query

    Returns:
        str: Formatted response with citations
    """
    if not retrieved_content or not retrieved_content.get("documents"):
        return "I couldn't find any relevant information to answer your question."

    documents = retrieved_content.get("documents", [])
    conversations = retrieved_content.get("conversations", [])

    # Format the response using enhanced document context
    response = enhanced_document_context(documents, query or "")

    # If we have conversations too, add them after documents
    if conversations:
        response += "\n\nRelevant conversation history:\n\n"
        for i, conv in enumerate(conversations, 1):
            message = conv.get("message", {})
            role = message.get("role", "user").capitalize()
            content = message.get("content", "No content")
            response += f"{role}: {content}\n\n"

    return response


def build_fallback_response(query, partial_results=None):
    """
    Build a fallback response when document retrieval fails or returns insufficient results.

    Args:
        query (str): The user's query
        partial_results (dict, optional): Any partial results that were retrieved

    Returns:
        str: Fallback response
    """
    # Base response
    response = [
        "I don't have enough specific information to give you a complete answer on this topic."
    ]

    # If we have partial results, acknowledge them
    if partial_results and partial_results.get("documents"):
        response.append("Based on limited information I do have:")

        # Extract what we know from partial results
        for doc in partial_results.get("documents", [])[:2]:
            title = doc.get("title", "") or doc.get("document", {}).get(
                "title", "Untitled"
            )
            snippet = (
                doc.get("content", "")
                or doc.get("text", "")
                or doc.get("document", {}).get("content", "")
            )

            # Include a brief snippet
            if snippet:
                snippet = snippet[:200] + "..." if len(snippet) > 200 else snippet
                response.append(f"- From {title}: {snippet}")

    # Suggest alternatives
    query_terms = query.lower().split()

    # Check for query type to give appropriate suggestions
    if any(term in query.lower() for term in ["how", "guidance", "steps", "tutorial"]):
        response.append(
            "To better assist you, I can provide general guidance on this topic if you'd like, or you could try asking a more specific question."
        )
    elif any(
        term in query.lower() for term in ["what", "definition", "explain", "describe"]
    ):
        response.append(
            "To better assist you, I can try to explain this concept in general terms, or you could try rephrasing your question to focus on a specific aspect."
        )
    elif any(
        term in query.lower() for term in ["compare", "difference", "versus", "vs"]
    ):
        response.append(
            "To better assist you, I can offer a general comparison based on common knowledge, or you could try asking about specific aspects you want to compare."
        )
    else:
        response.append(
            "To better assist you, please try rephrasing your question or providing more specific details about what you're looking for."
        )

    return "\n\n".join(response)


# Add an alias for backward compatibility with existing code
build_document_context = enhanced_document_context
