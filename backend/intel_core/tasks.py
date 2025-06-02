"""
Celery tasks for processing document uploads
"""

from celery import shared_task
from intel_core.utils.ingestion import ingest_urls, ingest_videos, ingest_pdfs
from intel_core.models import JobStatus, Document, DocumentSet
from utils.logging_utils import get_logger
from utils import coerce_uuid

logger = get_logger(__name__)


@shared_task(bind=True, name="process_url_upload")
def process_url_upload(
    self, urls, title=None, project_name="General", session_id=None, job_id=None
):
    """
    Process URL uploads in a background Celery task

    Args:
        urls (list): List of URLs to process
        title (str, optional): Title for the documents
        project_name (str): Project to associate documents with
        session_id (str): Session ID for tracking
        job_id (str): ID of the job status record

    Returns:
        int: Number of documents processed
    """
    job_uuid = coerce_uuid(job_id, "job_id")
    session_uuid = coerce_uuid(session_id, "session_id")
    if not job_uuid:
        logger.error("[UUID Sanity] Aborting task due to invalid job_id")
        return 0
    try:
        job = JobStatus.objects.get(job_id=job_uuid)
        job.status = "processing"
        job.stage = "chunking"
        job.progress = 10
        job.total_chunks = len(urls)
        job.save()

        # Process URLs
        total_urls = len(urls)
        processed_docs = []

        for i, url in enumerate(urls):
            job.current_chunk = i + 1
            job.progress = int(10 + (i / total_urls) * 80)
            job.message = f"Processing URL {i+1}/{total_urls}: {url}"
            job.save()

            # Process in smaller batches
            batch_result = ingest_urls(
                [url],
                title,
                project_name,
                str(session_uuid) if session_uuid else None,
                str(job_uuid),
            )
            processed_docs.extend(batch_result)

            # Log progress
            logger.info(
                f"Processed URL {i+1}/{total_urls}: {url} - Created {len(batch_result)} documents"
            )

        # Update final job status
        job.status = "completed"
        job.stage = "completed"
        job.progress = 100
        job.message = f"Successfully processed {len(urls)} URLs"
        job.result = {
            "success": True,
            "message": f"Successfully processed {len(processed_docs)} documents from {len(urls)} URLs",
            "document_count": len(processed_docs),
        }
        job.save()

        return len(processed_docs)
    except Exception as e:
        logger.error(f"Error in URL processing task: {str(e)}")
        if job_uuid:
            try:
                job = JobStatus.objects.get(job_id=job_uuid)
                job.status = "failed"
                job.message = str(e)
                job.save()
            except Exception:
                pass
        raise


@shared_task(bind=True, name="create_document_set_task")
def create_document_set_task(
    self,
    *,
    title,
    urls=None,
    videos=None,
    file_paths=None,
    tags=None,
    session_id=None,
    job_id=None,
):
    """Background task to ingest multiple sources into a DocumentSet."""
    logger.info(
        f"[Task Start] Triggered by DocumentSet title '{title}' | URLs: {urls} | Session: {session_id}"
    )
    urls = urls or []
    videos = videos or []
    file_paths = file_paths or []
    tags = tags or []
    job_uuid = coerce_uuid(job_id, "job_id")
    session_uuid = coerce_uuid(session_id, "session_id")
    if not job_uuid:
        logger.error("[UUID Sanity] Aborting task due to invalid job_id")
        return None
    try:
        job = JobStatus.objects.get(job_id=job_uuid)
        job.status = "processing"
        job.stage = "parsing"
        job.progress = 5
        job.total_chunks = len(urls) + len(videos) + len(file_paths)
        job.save()

        docs = []
        for i, url in enumerate(urls):
            job.current_chunk = i + 1
            job.stage = "chunking"
            job.progress = int(5 + (i / job.total_chunks) * 70)
            job.message = f"Loading URL {i+1}/{job.total_chunks}"
            job.save()
            docs.extend(
                ingest_urls(
                    [url],
                    title,
                    "General",
                    str(session_uuid) if session_uuid else None,
                    str(job_uuid),
                )
            )

        offset = len(urls)
        for j, vid in enumerate(videos):
            job.current_chunk = offset + j + 1
            job.stage = "chunking"
            job.progress = int(5 + ((offset + j) / job.total_chunks) * 70)
            job.message = f"Loading video {j+1}/{len(videos)}"
            job.save()
            docs.extend(
                ingest_videos(
                    [vid],
                    title,
                    "General",
                    str(session_uuid) if session_uuid else None,
                    str(job_uuid),
                )
            )

        offset += len(videos)
        for k, path in enumerate(file_paths):
            job.current_chunk = offset + k + 1
            job.stage = "chunking"
            job.progress = int(5 + ((offset + k) / job.total_chunks) * 70)
            job.message = f"Loading PDF {k+1}/{len(file_paths)}"
            job.save()
            docs.extend(
                ingest_pdfs(
                    [path],
                    title,
                    "General",
                    str(session_uuid) if session_uuid else None,
                    str(job_uuid),
                )
            )

        job.stage = "embedding"
        job.progress = 90
        job.save()

        document_set = DocumentSet.objects.create(
            title=title, urls=urls, videos=videos, tags=tags
        )
        for doc in docs:
            if isinstance(doc, Document):
                document_set.documents.add(doc)

        job.stage = "completed"
        job.progress = 100
        job.status = "completed"
        job.message = "Document set ingestion complete"
        job.save()

        return document_set.id
    except Exception as e:
        logger.error(f"Error in document set task: {str(e)}")
        if job_uuid:
            try:
                job = JobStatus.objects.get(job_id=job_uuid)
                job.status = "failed"
                job.message = str(e)
                job.save()
            except Exception:
                pass
        raise


@shared_task(bind=True, name="process_video_upload")
def process_video_upload(
    self, video_urls, title=None, project_name="General", session_id=None, job_id=None
):
    """
    Process YouTube video uploads in a background Celery task

    Args:
        video_urls (list): List of YouTube URLs to process
        title (str, optional): Title for the videos
        project_name (str): Project to associate documents with
        session_id (str): Session ID for tracking
        job_id (str): ID of the job status record

    Returns:
        int: Number of documents processed
    """
    job_uuid = coerce_uuid(job_id, "job_id")
    session_uuid = coerce_uuid(session_id, "session_id")
    if not job_uuid:
        logger.error("[UUID Sanity] Aborting task due to invalid job_id")
        return 0
    try:
        # Update job status to processing
        job = JobStatus.objects.get(job_id=job_uuid)
        job.status = "processing"
        job.stage = "chunking"
        job.progress = 10
        job.total_chunks = len(video_urls)
        job.save()

        # Process videos
        total_videos = len(video_urls)
        processed_docs = []

        for i, url in enumerate(video_urls):
            job.current_chunk = i + 1
            job.progress = int(10 + (i / total_videos) * 80)
            job.message = f"Processing video {i+1}/{total_videos}: {url}"
            job.save()

            # Videos take longer to process
            batch_result = ingest_videos(
                [url],
                title,
                project_name,
                str(session_uuid) if session_uuid else None,
                str(job_uuid),
            )
            processed_docs.extend(batch_result)

            # Log progress
            logger.info(
                f"Processed video {i+1}/{total_videos}: {url} - Created {len(batch_result)} documents"
            )

        # Update final job status
        job.status = "completed"
        job.stage = "completed"
        job.progress = 100
        job.message = f"Successfully processed {len(video_urls)} videos"
        job.result = {
            "success": True,
            "message": f"Successfully processed {len(processed_docs)} documents from {len(video_urls)} videos",
            "document_count": len(processed_docs),
        }
        job.save()

        return len(processed_docs)
    except Exception as e:
        logger.error(f"Error in video processing task: {str(e)}")
        if job_uuid:
            try:
                job = JobStatus.objects.get(job_id=job_uuid)
                job.status = "failed"
                job.message = str(e)
                job.save()
            except Exception:
                pass
        raise


@shared_task(bind=True, name="process_pdf_upload")
def process_pdf_upload(
    self, file_paths, title=None, project_name="General", session_id=None, job_id=None
):
    """
    Process PDF uploads in a background Celery task

    Args:
        file_paths (list): List of temporary file paths to process
        title (str, optional): Title for the PDFs
        project_name (str): Project to associate documents with
        session_id (str): Session ID for tracking
        job_id (str): ID of the job status record

    Returns:
        int: Number of documents processed
    """
    job_uuid = coerce_uuid(job_id, "job_id")
    session_uuid = coerce_uuid(session_id, "session_id")
    if not job_uuid:
        logger.error("[UUID Sanity] Aborting task due to invalid job_id")
        return 0
    try:
        # Update job status to processing
        job = JobStatus.objects.get(job_id=job_uuid)
        job.status = "processing"
        job.stage = "chunking"
        job.progress = 10
        job.total_chunks = len(file_paths)
        job.save()

        # Process PDFs
        total_pdfs = len(file_paths)
        processed_docs = []

        for i, file_path in enumerate(file_paths):
            job.current_chunk = i + 1
            job.progress = int(10 + (i / total_pdfs) * 80)
            job.message = f"Processing PDF {i+1}/{total_pdfs}"
            job.save()

            # PDFs process differently than URLs and videos
            # We'd need to modify this based on how your ingest_pdfs function works
            batch_result = ingest_pdfs(
                [file_path],
                title,
                project_name,
                str(session_uuid) if session_uuid else None,
                str(job_uuid),
            )
            processed_docs.extend(batch_result)

            # Log progress
            logger.info(
                f"Processed PDF {i+1}/{total_pdfs} - Created {len(batch_result)} documents"
            )

        # Update final job status
        job.status = "completed"
        job.stage = "completed"
        job.progress = 100
        job.message = f"Successfully processed {len(file_paths)} PDFs"
        job.result = {
            "success": True,
            "message": f"Successfully processed {len(processed_docs)} documents from {len(file_paths)} PDFs",
            "document_count": len(processed_docs),
        }
        job.save()

        return len(processed_docs)
    except Exception as e:
        logger.error(f"Error in PDF processing task: {str(e)}")
        if job_uuid:
            try:
                job = JobStatus.objects.get(job_id=job_uuid)
                job.status = "failed"
                job.message = str(e)
                job.save()
            except Exception:
                pass
        raise
