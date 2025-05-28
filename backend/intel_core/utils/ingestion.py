import logging

# Set up logging
logger = logging.getLogger("ingestion")


def ingest_pdfs(
    file_paths,
    title=None,
    project_name="General",
    session_id=None,
    job_id=None,
):
    """
    Ingest a batch of PDFs.

    Args:
        file_paths (list): List of PDF file paths.
        title (str, optional): Title to assign to the PDFs. If None, filenames will be used.
        project_name (str): Project name for grouping documents.
        session_id (str, optional): Session ID for tracking and retrieval.

    Returns:
        list: Processed document objects.
    """
    # Import inside function to avoid circular imports
    from intel_core.processors.pdf_loader import load_pdfs

    logger.info(f"Starting PDF ingestion of {len(file_paths)} files")
    try:
        processed_documents = load_pdfs(
            file_paths,
            user_provided_title=title,
            project_name=project_name,
            session_id=session_id,
            job_id=job_id,
        )
        logger.info(
            f"Ingested {len(processed_documents)} PDF chunks for project '{project_name}'"
        )
        return processed_documents
    except Exception as e:
        logger.error(f"Error ingesting PDFs: {str(e)}")
        return []


def ingest_urls(urls, title=None, project_name="General", session_id=None, job_id=None):
    """
    Ingest content from URLs.

    Args:
        urls (list): List of URLs to ingest.
        title (str, optional): Title to assign to the content. If None, will be extracted.
        project_name (str): Project name for grouping documents.
        session_id (str, optional): Session ID for tracking and retrieval.

    Returns:
        list: Processed document objects.
    """
    # Import inside function to avoid circular imports
    from intel_core.processors.url_loader import load_urls

    logger.info(f"Starting URL ingestion of {len(urls)} URLs")
    try:
        processed_documents = load_urls(
            urls,
            user_provided_title=title,
            project_name=project_name,
            session_id=session_id,
            job_id=job_id,
        )
        logger.info(
            f"Ingested {len(processed_documents)} URL chunks for project '{project_name}'"
        )
        return processed_documents
    except Exception as e:
        logger.error(f"Error ingesting URLs: {str(e)}")
        return []


def ingest_videos(video_urls, title=None, project_name="General", session_id=None, job_id=None):
    """
    Ingest YouTube videos.

    Args:
        video_urls (list): List of YouTube URLs to ingest.
        title (str, optional): Title to assign to the videos. If None, extracted from videos.
        project_name (str): Project name for grouping documents.
        session_id (str, optional): Session ID for tracking and retrieval.

    Returns:
        list: Processed document objects.
    """
    # Import inside function to avoid circular imports
    from intel_core.processors.video_loader import load_videos

    logger.info(f"Starting video ingestion of {len(video_urls)} videos")
    try:
        processed_documents = load_videos(
            video_urls,
            user_provided_title=title,
            project_name=project_name,
            session_id=session_id,
            job_id=job_id,
        )
        logger.info(
            f"Ingested {len(processed_documents)} video chunks for project '{project_name}'"
        )
        return processed_documents
    except Exception as e:
        logger.error(f"Error ingesting videos: {str(e)}")
        return []
