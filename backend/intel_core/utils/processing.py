import spacy
import uuid
import logging
import numpy as np
from openai import OpenAI
from intel_core.models import Document
from intel_core.core import clean_text, lemmatize_text, detect_topic
from mcp_core.models import Tag
from embeddings.helpers.helpers_io import save_embedding
from embeddings.helpers.helpers_processing import generate_embedding

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

def save_document_to_db(content, metadata, session_id=None):
    logger.info(f"🧐 Full Metadata: {metadata}")

    try:
        if not content or len(content.strip()) < 10:
            logger.error("❌ Document content is empty or too short")
            return None

        embedding = generate_embedding(content)
        if embedding is None:
            logger.warning("🔄 Retrying with content sample")
            sample_content = content[:5000]
            embedding = generate_embedding(sample_content)
            if embedding is None:
                logger.error("❌ Failed to embed even short content")
                return None

        title = metadata.get("title", "Untitled")
        slug = generate_unique_slug(title)
        session_id = metadata.get("session_id", session_id)

        logger.info(f"Session ID before querying: {session_id} | Type: {type(session_id)}")

        if isinstance(session_id, str):
            try:
                session_id = uuid.UUID(session_id)
            except Exception as e:
                logger.warning(f"⚠️ Invalid session_id format: {e}")
                session_id = None

        summary = generate_summary(content)
        source_type = metadata.get("source_type", "Unknown")

        # Use update_or_create to avoid duplicates
        document, created = Document.objects.update_or_create(
            slug=slug,
            defaults={
                "content": content,
                "title": title,
                "source_type": source_type,
                "source_url": metadata.get("source_url"),
                "metadata": metadata,
                "session_id": session_id,
                "description": f"Ingested from {source_type} - {title}",
                "summary": summary,
            },
        )

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

        return document

    except Exception as e:
        logger.error(f"❌ Error saving document to DB: {e}")
        return None


# Process PDFs
def process_pdfs(pdf, pdf_title, project_name, session_id):
    logger = logging.getLogger("django")
    try:
        logger.info(f"📄 Processing PDF: {pdf_title}")
        cleaned_text = clean_text(pdf.page_content)
        lemmatized_text = lemmatize_text(cleaned_text, nlp)

        metadata_dict = {
            "title": pdf_title,
            "project": project_name,
            "source_type": "pdf",
            "session_id": session_id,
        }

        # Add summary
        metadata_dict["summary"] = generate_summary(lemmatized_text)

        logger.info(f"📝 PDF content sample: {lemmatized_text[:200]}...")
        logger.info(f"🔍 PDF metadata: {metadata_dict}")

        document = save_document_to_db(lemmatized_text, metadata_dict, session_id)
        logger.info(f"✅ PDF processed and saved: {pdf_title}")

        return document
    except Exception as e:
        logger.error(f"❌ Error processing PDF: {str(e)}")
        return Document(
            content="Error processing PDF content",
            metadata={"title": pdf_title, "error": str(e)},
        )


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
