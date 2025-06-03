"""Document ingestion service consolidating loaders."""

import os
from utils.logging_utils import get_logger
import warnings
from typing import List
from urllib.parse import urlparse

from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from intel_core.utils.processing import (
    process_pdfs,
    process_urls,
    process_videos,
)
from intel_core.models import (
    Document,
    DocumentChunk,
    DocumentProgress,
    JobStatus,
)
from intel_core.core import clean_text
from intel_core.helpers.document_helpers import fetch_url, extract_visible_text
from prompts.utils.token_helpers import count_tokens
from intel_core.helpers.youtube_video_helper import process_youtube_video

logger = get_logger("document_service")
warnings.filterwarnings("ignore", category=Warning)


def _update_job(job_id: str | None, *, current: int, total: int, message: str):
    """Helper to update JobStatus progress if job_id provided."""
    if not job_id:
        return
    try:
        job = JobStatus.objects.get(job_id=job_id)
        job.current_chunk = current
        job.total_chunks = total
        job.progress = int(current / total * 100) if total else 0
        job.stage = "chunking"
        job.message = message
        job.save()
    except JobStatus.DoesNotExist:
        pass


def ingest_pdfs(
    file_paths: List[str],
    user_provided_title: str | None = None,
    project_name: str = "General",
    session_id: str | None = None,
    job_id: str | None = None,
):
    logger.info(f"Loading {len(file_paths)} PDFs for project '{project_name}'")
    if session_id:
        logger.info(f"Using session_id: {session_id}")

    processed_documents = []
    for file_path in file_paths:
        progress = None
        try:
            file_name = os.path.basename(file_path)
            pdf_title = user_provided_title or os.path.splitext(file_name)[0]

            logger.info(f"Processing PDF: {pdf_title} from {file_path}")

            loader = PDFPlumberLoader(file_path=file_path)
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=500
            )
            pdf_list = loader.load_and_split(text_splitter)

            if not pdf_list:
                logger.warning(f"No content extracted from PDF: {file_path}")
                continue

            logger.info(f"Successfully extracted {len(pdf_list)} chunks from PDF")

            progress = DocumentProgress.objects.create(
                title=pdf_title,
                total_chunks=len(pdf_list),
                status="in_progress",
            )
            failed_chunks = set()

            for i, pdf in enumerate(pdf_list):
                pdf.metadata.update(
                    {
                        "title": pdf_title,
                        "source_type": "PDF",
                        "source_path": file_path,
                        "project": project_name,
                        "session_id": session_id,
                        "chunk_index": i,
                        "total_chunks": len(pdf_list),
                        "progress_id": str(progress.progress_id),
                    }
                )

                cleaned = clean_text(pdf.page_content)
                if not cleaned or len(cleaned.split()) < 20:
                    logger.warning(
                        f"Skipping chunk {i+1}/{len(pdf_list)} for '{pdf_title}' - too short"
                    )
                    failed_chunks.add(i)
                    progress.failed_chunks = list(failed_chunks)
                    progress.save()
                    continue

                processed_document = process_pdfs(
                    pdf, pdf_title, project_name, session_id
                )

                if not processed_document and i not in failed_chunks:
                    logger.info(
                        f"Retrying chunk {i+1}/{len(pdf_list)} for '{pdf_title}'"
                    )
                    processed_document = process_pdfs(
                        pdf, pdf_title, project_name, session_id
                    )

                if processed_document:
                    processed_documents.append(processed_document)
                    progress.processed += 1
                    logger.info(f"Successfully processed chunk {i+1}/{len(pdf_list)}")
                    _update_job(
                        job_id,
                        current=progress.processed,
                        total=progress.total_chunks,
                        message=f"Successfully processed chunk {i+1}/{len(pdf_list)}",
                    )
                else:
                    logger.error(
                        f"Failed to process chunk {i+1}/{len(pdf_list)} for '{pdf_title}'",
                        exc_info=True,
                    )
                    failed_chunks.add(i)

                progress.failed_chunks = list(failed_chunks)
                progress.save()

            progress.status = "completed" if not failed_chunks else "failed"
            progress.save()
            _update_job(
                job_id,
                current=progress.total_chunks,
                total=progress.total_chunks,
                message="PDF processing complete",
            )

        except Exception as e:
            logger.error(f"Failed to process PDF {file_path}: {e}")
            if "progress" in locals() and isinstance(progress, DocumentProgress):
                progress.status = "failed"
                progress.error_message = str(e)
                progress.save()

    logger.info(f"Completed processing {len(processed_documents)} PDF chunks")
    return processed_documents


def _extract_page_title(content: str, url: str) -> str:
    from bs4 import BeautifulSoup as Soup

    try:
        soup = Soup(content, "html.parser")
        title_tag = soup.find("title")
        if title_tag and title_tag.text.strip():
            return title_tag.text.strip()
        domain = urlparse(url).netloc
        return domain if domain else os.path.basename(url)
    except Exception as e:
        logger.warning(f"Could not extract title from {url}: {e}")
        return os.path.basename(url)


def ingest_urls(
    urls: List[str],
    user_provided_title: str | None = None,
    project_name: str = "General",
    session_id: str | None = None,
    job_id: str | None = None,
):
    logger.info(f"Loading {len(urls)} URLs for project '{project_name}'")
    if session_id:
        logger.info(f"Using session_id: {session_id}")

    processed_documents = []
    for url in urls:
        try:
            logger.info(f"Processing URL: {url}")

            existing_doc = Document.objects.filter(source_url=url).first()
            if existing_doc and DocumentChunk.objects.filter(document=existing_doc).exists():
                logger.warning(f"[Ingest] Skipping {url} — chunks already exist.")
                processed_documents.append(
                    {
                        "message": "Ingestion complete",
                        "document_id": str(existing_doc.id),
                        "embedded_chunks": existing_doc.chunks.filter(embedding__isnull=False).count(),
                        "total_chunks": existing_doc.chunks.count(),
                        "summary": existing_doc.summary,
                    }
                )
                continue

            content = fetch_url(url)
            if not content:
                logger.warning(f"Could not fetch content for URL: {url}")
                continue

            if not user_provided_title:
                page_title = _extract_page_title(content, url)
                logger.info(f"Extracted title: {page_title}")
            else:
                page_title = user_provided_title
                logger.info(f"Using provided title: {page_title}")

            visible_text = extract_visible_text(content)
            logger.debug(f"[Ingest] Source URL: {url}")
            logger.debug(f"[Ingest] Cleaned text length: {len(visible_text)}")
            logger.debug(f"[Ingest] First 300 chars: {visible_text[:300]}")
            logger.debug(f"[Ingest] Token estimate: {count_tokens(visible_text)}")
            if not visible_text or len(visible_text.strip()) < 50:
                logger.warning(
                    f"Insufficient text content extracted from URL: {url}"
                )
                continue

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000, chunk_overlap=200
            )
            chunks = text_splitter.split_text(visible_text)
            if not chunks:
                logger.warning(f"No chunks generated from URL: {url}")
                continue

            logger.info(f"Successfully extracted {len(chunks)} chunks from URL")

            for i, chunk in enumerate(chunks):
                metadata = {
                    "title": page_title,
                    "source_type": "URL",
                    "source_url": url,
                    "project": project_name,
                    "session_id": session_id,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                }

                processed_doc = process_urls(
                    chunk, page_title, project_name, metadata, session_id
                )
                if processed_doc:
                    processed_documents.append(processed_doc)
                    logger.info(f"Successfully processed chunk {i+1}/{len(chunks)}")
                    _update_job(
                        job_id,
                        current=i + 1,
                        total=len(chunks),
                        message=f"Successfully processed chunk {i+1}/{len(chunks)}",
                    )
                else:
                    logger.warning(f"Failed to process chunk {i+1}/{len(chunks)}")
        except Exception as e:
            logger.error(f"Failed to process URL {url}: {e}")

    logger.info(f"Completed processing {len(processed_documents)} URL chunks")
    return processed_documents


def ingest_videos(
    video_urls: List[str],
    user_provided_title: str | None = None,
    project_name: str = "General",
    session_id: str | None = None,
    job_id: str | None = None,
):
    """Ingest a list of YouTube videos and return serialized info."""

    processed_documents: list[dict] = []

    for index, url in enumerate(video_urls):
        try:
            existing_doc = Document.objects.filter(source_url=url).first()
            if existing_doc and DocumentChunk.objects.filter(document=existing_doc).exists():
                logger.warning(f"[Ingest] Skipping {url} — chunks already exist.")
                processed_documents.append(existing_doc)
                continue

            chunks = process_youtube_video(url)
            if not chunks:
                logger.warning(f"Could not fetch content for video: {url}")
                processed_documents.append(
                    {
                        "status": "skipped",
                        "reason": "Transcript could not be retrieved",
                        "url": url,
                    }
                )
                continue

            video_title = user_provided_title or "Uploaded Video"
            transcript_text = " ".join(chunks)
            if transcript_text.strip() == "":
                logger.warning("Transcript text is empty — skipping document creation.")
                processed_documents.append(
                    {
                        "status": "skipped",
                        "reason": "Transcript could not be retrieved",
                        "url": url,
                    }
                )
                continue

            document = {
                "page_content": transcript_text,
                "metadata": {
                    "title": video_title,
                    "source_type": "YouTube",
                    "source_url": url,
                    "project": project_name,
                    "session_id": session_id,
                },
            }
            logger.info("[Router] Reached document_service.ingest(). source_type=%s", document)
            processed_document = process_videos(
                document,
                video_title=video_title,
                project_name=project_name,
                session_id=session_id,
            )

            if processed_document:
                chunk_total = processed_document.chunks.count()
                embedded = processed_document.chunks.filter(embedding__isnull=False).count()
                logger.info(
                    f"[Ingest] {embedded}/{chunk_total} chunks embedded for {processed_document.title}"
                )
                processed_documents.append(
                    {
                        "message": "Ingestion complete",
                        "document_id": str(processed_document.id),
                        "embedded_chunks": embedded,
                        "total_chunks": chunk_total,
                        "summary": processed_document.summary,
                    }
                )
            else:
                processed_documents.append(
                    {
                        "status": "skipped",
                        "reason": "Transcript could not be retrieved",
                        "url": url,
                    }
                )

            _update_job(
                job_id,
                current=index + 1,
                total=len(video_urls),
                message=f"Processed video {index + 1}/{len(video_urls)}",
            )

        except Exception as e:
            logger.error(f"Failed to process YouTube video {url}: {e}")

    return processed_documents


def ingest_documents(*args, **kwargs):
    """Generic ingestion dispatch."""
    if kwargs.get("file_paths"):
        return ingest_pdfs(**kwargs)
    if kwargs.get("urls"):
        return ingest_urls(**kwargs)
    if kwargs.get("video_urls"):
        return ingest_videos(**kwargs)
    
    raise ValueError("No valid ingestion parameters provided")
