import os
import requests
import logging
from bs4 import BeautifulSoup as Soup
from urllib.parse import urlparse
from langchain_community.document_loaders import RecursiveUrlLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from retrying import retry
import warnings
from intel_core.utils.processing import process_urls
from intel_core.helpers.document_helpers import fetch_url, extract_visible_text

# Set up logging
logger = logging.getLogger("url_loader")

# Suppress only the specific warning from BeautifulSoup
warnings.filterwarnings("ignore", category=Warning)


def extract_page_title(content, url):
    """
    Extract title from HTML content.

    Args:
        content (str): HTML content
        url (str): URL for fallback

    Returns:
        str: Extracted title or URL as fallback
    """
    try:
        soup = Soup(content, "html.parser")
        title_tag = soup.find("title")
        if title_tag and title_tag.text.strip():
            return title_tag.text.strip()
        else:
            # Try to use domain as title
            domain = urlparse(url).netloc
            return domain if domain else os.path.basename(url)
    except Exception as e:
        logger.warning(f"Could not extract title from {url}: {e}")
        return os.path.basename(url)


def load_urls(urls, user_provided_title=None, project_name="General", session_id=None):
    """
    Load and process documents from the given URLs.

    Args:
        urls (list): List of URLs to process.
        user_provided_title (str, optional): Title to assign to the URLs. If None,
                                           page title will be extracted.
        project_name (str): Name of the project for metadata.
        session_id (str): UUID of the session for tracking.

    Returns:
        list: List of processed Document objects.
    """
    logger.info(f"Loading {len(urls)} URLs for project '{project_name}'")
    if session_id:
        logger.info(f"Using session_id: {session_id}")

    processed_documents = []

    for url in urls:
        try:
            logger.info(f"Processing URL: {url}")

            # Fetch content from the URL (handles JavaScript-rendered content)
            content = fetch_url(url)
            if not content:
                logger.warning(f"Could not fetch content for URL: {url}")
                continue

            # Extract page title if user didn't provide one
            if not user_provided_title:
                page_title = extract_page_title(content, url)
                logger.info(f"Extracted title: {page_title}")
            else:
                page_title = user_provided_title
                logger.info(f"Using provided title: {page_title}")

            # Extract visible text
            visible_text = extract_visible_text(content)
            if not visible_text or len(visible_text.strip()) < 50:
                logger.warning(f"Insufficient text content extracted from URL: {url}")
                continue

            # Split content into manageable chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=200
            )
            chunks = text_splitter.split_text(visible_text)

            if not chunks or len(chunks) == 0:
                logger.warning(f"No chunks generated from URL: {url}")
                continue

            logger.info(f"Successfully extracted {len(chunks)} chunks from URL")

            # Process each chunk and save it
            for i, chunk in enumerate(chunks):
                # Create metadata
                metadata = {
                    "title": page_title,
                    "source_type": "URL",
                    "source_url": url,
                    "project": project_name,
                    "session_id": session_id,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                }

                # Process the URL chunk
                processed_doc = process_urls(
                    chunk, page_title, project_name, metadata, session_id
                )

                if processed_doc:
                    processed_documents.append(processed_doc)
                    logger.info(f"Successfully processed chunk {i+1}/{len(chunks)}")
                else:
                    logger.warning(f"Failed to process chunk {i+1}/{len(chunks)}")

        except Exception as e:
            logger.error(f"Failed to process URL {url}: {e}")
            # Continue with other URLs even if one fails

    logger.info(f"Completed processing {len(processed_documents)} URL chunks")
    return processed_documents
