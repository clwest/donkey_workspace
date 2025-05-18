"""
Celery tasks for processing document uploads
"""

from celery import shared_task
from intel_core.utils.ingestion import ingest_urls, ingest_videos, ingest_pdfs
from intel_core.models import JobStatus
import logging

logger = logging.getLogger(__name__)


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
    try:
        # Update job status to processing
        job = JobStatus.objects.get(job_id=job_id)
        job.status = "processing"
        job.progress = 10
        job.save()

        # Process URLs
        total_urls = len(urls)
        processed_docs = []

        for i, url in enumerate(urls):
            # Update progress for each URL
            progress = int(10 + (i / total_urls) * 80)  # Progress from 10% to 90%
            job.progress = progress
            job.message = f"Processing URL {i+1}/{total_urls}: {url}"
            job.save()

            # Process in smaller batches
            batch_result = ingest_urls([url], title, project_name, session_id)
            processed_docs.extend(batch_result)

            # Log progress
            logger.info(
                f"Processed URL {i+1}/{total_urls}: {url} - Created {len(batch_result)} documents"
            )

        # Update final job status
        job.status = "completed"
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
        if job_id:
            try:
                job = JobStatus.objects.get(job_id=job_id)
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
    try:
        # Update job status to processing
        job = JobStatus.objects.get(job_id=job_id)
        job.status = "processing"
        job.progress = 10
        job.save()

        # Process videos
        total_videos = len(video_urls)
        processed_docs = []

        for i, url in enumerate(video_urls):
            # Update progress for each video
            progress = int(10 + (i / total_videos) * 80)
            job.progress = progress
            job.message = f"Processing video {i+1}/{total_videos}: {url}"
            job.save()

            # Videos take longer to process
            batch_result = ingest_videos([url], title, project_name, session_id)
            processed_docs.extend(batch_result)

            # Log progress
            logger.info(
                f"Processed video {i+1}/{total_videos}: {url} - Created {len(batch_result)} documents"
            )

        # Update final job status
        job.status = "completed"
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
        if job_id:
            try:
                job = JobStatus.objects.get(job_id=job_id)
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
    try:
        # Update job status to processing
        job = JobStatus.objects.get(job_id=job_id)
        job.status = "processing"
        job.progress = 10
        job.save()

        # Process PDFs
        total_pdfs = len(file_paths)
        processed_docs = []

        for i, file_path in enumerate(file_paths):
            # Update progress for each PDF
            progress = int(10 + (i / total_pdfs) * 80)
            job.progress = progress
            job.message = f"Processing PDF {i+1}/{total_pdfs}"
            job.save()

            # PDFs process differently than URLs and videos
            # We'd need to modify this based on how your ingest_pdfs function works
            batch_result = ingest_pdfs([file_path], title, project_name, session_id)
            processed_docs.extend(batch_result)

            # Log progress
            logger.info(
                f"Processed PDF {i+1}/{total_pdfs} - Created {len(batch_result)} documents"
            )

        # Update final job status
        job.status = "completed"
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
        if job_id:
            try:
                job = JobStatus.objects.get(job_id=job_id)
                job.status = "failed"
                job.message = str(e)
                job.save()
            except Exception:
                pass
        raise
