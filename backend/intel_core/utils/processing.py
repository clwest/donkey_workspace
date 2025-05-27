import spacy
import uuid
import logging
import numpy as np
from openai import OpenAI
from intel_core.models import Document
from django.db import IntegrityError
from intel_core.core import clean_text, lemmatize_text, detect_topic
from mcp_core.models import Tag
from embeddings.helpers.helpers_io import save_embedding
from embeddings.sentence_transformer_service import get_sentence_transformer
from intel_core.models import EmbeddingMetadata

sentence_transformer = get_sentence_transformer()

logger = logging.getLogger("django")
client = OpenAI()
nlp = spacy.load("en_core_web_sm")


def generate_summary(text: str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that summarizes documents in 2-3 sentences.",
                },
                {
                    "role": "user",
                    "content": f"Summarize the following document:\n\n{text[:3000]}",
                },
            ],
            temperature=0.4,
            max_tokens=160,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.warning(f"❌ Failed to generate summary: {e}")
        return None


from django.utils.text import slugify
def generate_unique_slug(title):
    base_slug = slugify(title)
    slug = base_slug
    counter = 1
    while Document.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1
    return slug

from embeddings.document_services.chunking import (
    generate_chunks,
    generate_chunk_fingerprint,
)
from prompts.utils.token_helpers import count_tokens, EMBEDDING_MODEL
from intel_core.models import DocumentChunk


def _create_document_chunks(document: Document):
    """Create DocumentChunk objects for ``document`` if none exist."""
    if DocumentChunk.objects.filter(document=document).exists():
        return

    chunks = generate_chunks(document.content)
    for i, chunk in enumerate(chunks):
        fingerprint = generate_chunk_fingerprint(chunk)
        try:
            DocumentChunk.objects.create(
                document=document,
                order=i,
                text=chunk,
                tokens=count_tokens(chunk),
                chunk_type="body",
                fingerprint=fingerprint,
            )
        except IntegrityError:
            logger.warning(
                f"Duplicate fingerprint for chunk {i} on document {document.id}, skipping"
            )


def _embed_document_chunks(document: Document):
    """Generate embeddings for chunks lacking vectors."""
    unembedded = DocumentChunk.objects.filter(document=document, embedding__isnull=True)
    for chunk in unembedded:
        try:
            vector = sentence_transformer.encode(chunk.text)
        except Exception as e:  # pragma: no cover - embedding errors
            logger.warning(f"Failed to embed chunk {chunk.id}: {e}")
            continue

        if not vector:
            continue
        if hasattr(vector, "tolist"):
            vector = vector.tolist()

        meta = EmbeddingMetadata.objects.create(
            model_used=EMBEDDING_MODEL,
            num_tokens=chunk.tokens,
            vector=vector,
            status="completed",
            source=document.source_type,
        )
        chunk.embedding = meta
        chunk.save(update_fields=["embedding"])
        try:
            save_embedding(chunk, vector)
        except Exception as e:
            logger.warning(f"Failed to register embedding for chunk {chunk.id}: {e}")


def save_document_to_db(content, metadata, session_id=None):
    logger.info(f"🧐 Full Metadata: {metadata}")

    try:
        if not content or len(content.strip()) < 10:
            logger.error("❌ Document content is empty or too short")
            return None

        embedding = sentence_transformer.encode(content)
        if embedding is None:
            logger.warning("🔄 Retrying with content sample")
            sample_content = content[:5000]
            embedding = sentence_transformer.encode(sample_content)
            if embedding is None:
                logger.error("❌ Failed to embed even short content")
                return None

        title = metadata.get("title", "Untitled")
        slug = generate_unique_slug(title)
        session_id = metadata.get("session_id", session_id)
        if not session_id or str(session_id) == "00000000-0000-0000-0000-000000000000":
            session_id = uuid.uuid4()

        if not metadata.get("source_url"):
            file_hint = metadata.get("source_path") or title
            metadata["source_url"] = f"uploaded://{file_hint}"
            logger.info(f"ℹ️ source_url missing, using placeholder {metadata['source_url']}")

        logger.info(f"Session ID before querying: {session_id} | Type: {type(session_id)}")

        if isinstance(session_id, str):
            try:
                session_id = uuid.UUID(session_id)
            except Exception as e:
                logger.warning(f"⚠️ Invalid session_id format: {e}")
                session_id = uuid.uuid4()

        summary = generate_summary(content)
        source_type = metadata.get("source_type", "Unknown")

        existing = None
        if metadata.get("source_url"):
            existing = Document.objects.filter(source_url=metadata["source_url"]).first()
        if not existing and metadata.get("source_path"):
            existing = Document.objects.filter(metadata__source_path=metadata["source_path"]).first()

        if existing:
            for field, value in {
                "content": content,
                "title": title,
                "source_type": source_type,
                "source_url": metadata.get("source_url"),
                "metadata": metadata,
                "session_id": session_id,
                "description": f"Ingested from {source_type} - {title}",
                "summary": summary,
            }.items():
                setattr(existing, field, value)
            existing.save()
            document = existing
            created = False
        else:
            document = Document.objects.create(
                slug=slug,
                content=content,
                title=title,
                source_type=source_type,
                source_url=metadata.get("source_url"),
                metadata=metadata,
                session_id=session_id,
                description=f"Ingested from {source_type} - {title}",
                summary=summary,
            )
            created = True

        if created:
            logger.info(f"✅ Created new Document: {document.title}")
        else:
            logger.info(f"♻️ Updated existing Document: {document.title}")

        if hasattr(document, "tags"):
            detected_tag = detect_topic(content)
            if detected_tag:
                tag = Tag.objects.filter(name=detected_tag).first()
                if tag:
                    document.tags.add(tag)

        if embedding is not None:
            embedding_list = (
                embedding.tolist() if isinstance(embedding, np.ndarray) else embedding
            )
            embedding_id = save_embedding(document, embedding_list)
            logger.info(f"✅ Saved embedding: {embedding_id} for document: {document.title}")

        _create_document_chunks(document)
        _embed_document_chunks(document)

        return document

    except Exception as e:
        logger.error(f"❌ Error saving document to DB: {e}")
        return None


# Process PDFs
def process_pdfs(pdf, pdf_title, project_name, session_id):
    logger = logging.getLogger("django")
    try:
        chunk_idx = pdf.metadata.get("chunk_index")
        total_chunks = pdf.metadata.get("total_chunks")
        logger.info(f"📄 Processing PDF: {pdf_title} [chunk {chunk_idx}/{total_chunks}]")
        cleaned_text = clean_text(pdf.page_content)
        lemmatized_text = lemmatize_text(cleaned_text, nlp)

        metadata_dict = {
            "title": pdf_title,
            "project": project_name,
            "source_type": "pdf",
            "session_id": session_id,
            "chunk_index": chunk_idx,
            "total_chunks": total_chunks,
            "source_path": pdf.metadata.get("source_path"),
        }

        # Add summary
        metadata_dict["summary"] = generate_summary(lemmatized_text)

        logger.info(f"📝 PDF content sample: {lemmatized_text[:200]}...")
        logger.info(f"🔍 PDF metadata: {metadata_dict}")

        document = save_document_to_db(lemmatized_text, metadata_dict, session_id)
        if document is None:
            logger.error(
                f"❌ Failed to save PDF chunk {chunk_idx}/{total_chunks} for '{pdf_title}'"
            )
            return None

        logger.info(f"✅ PDF processed and saved: {pdf_title} [chunk {chunk_idx}/{total_chunks}]")

        return document
    except Exception as e:
        logger.exception(
            f"❌ Exception processing PDF chunk {pdf_title} [chunk {chunk_idx}/{total_chunks}]: {e}"
        )
        return None


# Process URLs
def process_urls(content, url_title, project_name, metadata, session_id):
    logger = logging.getLogger("django")
    try:
        logger.info(f"🌐 Processing URL: {url_title}")
        cleaned_text = clean_text(content)
        lemmatized_text = lemmatize_text(cleaned_text, nlp)

        metadata.update(
            {
                "title": url_title,
                "project": project_name,
                "source_type": "url",
                "session_id": session_id,
                "summary": generate_summary(lemmatized_text),
            }
        )

        logger.info(f"📝 URL content sample: {lemmatized_text[:200]}...")
        logger.info(f"🔍 URL metadata: {metadata}")

        document = save_document_to_db(lemmatized_text, metadata, session_id)
        logger.info(f"✅ URL processed and saved: {url_title}")

        return document
    except Exception as e:
        logger.error(f"❌ Error processing URL: {str(e)}")
        return Document(
            content="Error processing URL content",
            metadata={"title": url_title, "error": str(e)},
        )


# Process Videos
def process_videos(video, video_title, project_name, session_id):
    logger = logging.getLogger("django")
    try:
        logger.info(f"📹 Processing video: {video_title}")
        cleaned_text = clean_text(video["page_content"])
        lemmatized_text = lemmatize_text(cleaned_text, nlp)
        metadata = video["metadata"]

        metadata.update(
            {
                "title": video_title,
                "project": project_name,
                "session_id": session_id,
                "source_type": "video",
                "summary": generate_summary(lemmatized_text),
            }
        )

        logger.info(f"📝 Video content sample: {lemmatized_text[:200]}...")
        logger.info(f"🔍 Video metadata: {metadata}")

        document = save_document_to_db(lemmatized_text, metadata, session_id)
        logger.info(f"✅ Video processed and saved: {video_title}")

        return document
    except Exception as e:
        logger.error(f"❌ Error processing video: {str(e)}")
        return Document(
            content="Error processing video content",
            metadata={"title": video_title, "error": str(e)},
        )
