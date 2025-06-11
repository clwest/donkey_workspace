from utils.logging_utils import get_logger
import re
import uuid

import numpy as np
import spacy
from celery import current_app
import time
from django.conf import settings
from django.db import IntegrityError
from embeddings.helpers.helpers_io import (
    get_embedding_for_text,
    save_embedding,
)
from intel_core.core import clean_text, detect_topic, lemmatize_text
from intel_core.models import Document, EmbeddingMetadata
from mcp_core.models import Tag
from openai import OpenAI

logger = get_logger("intel_core.processing")
client = OpenAI()
nlp = spacy.load("en_core_web_sm")


def is_celery_running() -> bool:
    """Check if a Celery worker is online."""
    try:
        insp = current_app.control.inspect()
        stats = insp.stats()
        return bool(stats)
    except Exception:
        return False


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
    clean_and_score_chunk,
    generate_chunk_fingerprint,
    generate_chunks,
)
from intel_core.models import DocumentChunk

# Import directly to avoid circular dependency triggered via
# ``intel_core.services.__init__`` which pulls in ``DocumentService``.
from memory.models import SymbolicMemoryAnchor

# Import directly to avoid circular dependency triggered via
# ``intel_core.services.__init__`` which pulls in ``DocumentService``.
from intel_core.services.acronym_glossary_service import AcronymGlossaryService
from intel_core.utils.glossary_tagging import _match_anchor


def compute_glossary_score(text: str, anchors=None):
    """Return (score, matched_slugs) for glossary anchors in ``text``."""
    if anchors is None:
        anchors = SymbolicMemoryAnchor.objects.all().prefetch_related("tags")
    text_lower = text.lower()
    matched = []
    words = text_lower.split()
    word_set = set(words)
    for anc in anchors:
        if anc.slug.lower() in text_lower or anc.label.lower() in text_lower:
            matched.append(anc.slug)
            continue
        tag_slugs = set(anc.tags.values_list("slug", flat=True))
        tag_names = set(anc.tags.values_list("name", flat=True))
        if word_set.intersection(tag_slugs) or word_set.intersection(tag_names):
            matched.append(anc.slug)
            continue
        m, _ = _match_anchor(anc, text)
        if m:
            matched.append(anc.slug)
    score = len(matched) / max(len(anchors), 1)

    if matched:
        density = len(matched) / max(len(words), 1)
        score = max(score, density)
        score = max(score, len(matched) / 10)
        score = max(score, 0.1)

    score = min(score, 1.0)
    return round(score, 2), matched


from prompts.utils.token_helpers import EMBEDDING_MODEL, count_tokens


def _create_document_chunks(document: Document):
    from embeddings.tasks import embed_and_store

    """Create DocumentChunk objects for ``document`` if none exist."""
    if DocumentChunk.objects.filter(document=document).exists():
        logger.info(
            "[Chunk Filter] %s already has chunks — skipping creation", document.id
        )
        return

    meta = document.metadata or {}
    progress_id = meta.get("progress_id")
    progress = None
    if progress_id:
        from intel_core.models import DocumentProgress

        progress = DocumentProgress.objects.filter(progress_id=progress_id).first()
    retry_attempts = meta.get("chunk_retry_attempts", 0)

    chunks = generate_chunks(document.content)
    chunks = AcronymGlossaryService.insert_glossary_chunk(chunks)
    anchors = list(SymbolicMemoryAnchor.objects.all().prefetch_related("tags"))
    queued_chunks = []
    if not chunks and document.summary:
        try:
            fallback_text = document.summary
            fingerprint = generate_chunk_fingerprint(fallback_text)
            new_chunk = DocumentChunk.objects.create(
                document=document,
                order=0,
                text=fallback_text,
                tokens=count_tokens(fallback_text),
                chunk_type="summary",
                fingerprint=fingerprint,
                force_embed=True,
            )
            new_chunk.embedding_status = "pending"
            new_chunk.save(update_fields=["embedding_status"])
            embed_and_store.delay(str(new_chunk.id))
            chunks = [fallback_text]
            queued_chunks.append(new_chunk.id)
            logger.warning("[Fallback] Injected synthetic summary chunk.")
        except Exception:
            logger.exception("Failed to inject synthetic summary chunk")
    short_candidates: list[tuple[int, dict]] = []
    skipped = 0
    for i, chunk in enumerate(chunks):
        info = clean_and_score_chunk(chunk, chunk_index=i)
        if not info["keep"]:
            skipped += 1
            logger.debug(
                "⏭️ Skipping chunk %d (%d chars, %s) reason=%s score=%.2f",
                i,
                len(chunk),
                document.source_type,
                info.get("reason"),
                info.get("score", 0.0),
            )
            logger.info(
                "[Chunk Filter] %s chunk %d skipped: %s (%.2f)",
                document.id,
                i,
                info.get("reason", "unknown").upper(),
                info.get("score", 0.0),
            )
            if info.get("reason") in ("too_short", "short_low_quality"):
                short_candidates.append((i, info))
            if not getattr(settings, "DISABLE_CHUNK_SKIP_FILTERS", False):
                continue
            logger.debug("⚠️ Filter bypass enabled — keeping chunk %d", i)
        fingerprint = generate_chunk_fingerprint(info["text"])
        anchor = None
        if "refers to" in info["text"].lower():
            match = re.match(r"([A-Z]{2,})\s+refers to", info["text"])
            if match:
                slug = match.group(1).lower()
                anchor, _ = SymbolicMemoryAnchor.objects.get_or_create(
                    slug=slug, defaults={"label": match.group(1)}
                )
        try:
            glossary_score, matched = compute_glossary_score(info["text"], anchors)
            new_chunk = DocumentChunk.objects.create(
                document=document,
                order=i,
                text=info["text"],
                tokens=count_tokens(info["text"]),
                chunk_type="body",
                is_glossary="refers to" in info["text"].lower(),
                tags=["glossary"] if "refers to" in info["text"].lower() else [],
                fingerprint=fingerprint,
                anchor=anchor,
                glossary_score=glossary_score,
                matched_anchors=matched,
                force_embed=getattr(settings, "DISABLE_CHUNK_SKIP_FILTERS", False),
            )
            logger.debug(
                f"🧠 Chunk created: {new_chunk.id} for Document {document.id} | text preview: {new_chunk.text[:60]}"
            )
            logger.debug(f"🚀 Scheduling embedding for chunk {new_chunk.id}")
            new_chunk.embedding_status = "pending"
            new_chunk.save(update_fields=["embedding_status"])
            logger.info(f"📦 Queuing chunk for embedding: {new_chunk.id}")
            try:
                embed_and_store.delay(str(new_chunk.id))
                queued_chunks.append(new_chunk.id)
            except Exception as e:
                logger.warning(
                    f"Failed to queue embedding task for chunk {new_chunk.id}: {e}"
                )
        except IntegrityError:
            logger.warning(
                f"🔁 Duplicate fingerprint {fingerprint} for chunk {i} on document {document.id}, skipping"
            )

    if not queued_chunks and short_candidates:
        logger.warning(
            "🟠 No long chunks queued; retrying with %d short candidates",
            len(short_candidates),
        )
        retry_attempts += 1
        if progress:
            progress.error_message = f"retry_attempts:{retry_attempts}"
            progress.save(update_fields=["error_message"])
        meta["chunk_retry_attempts"] = retry_attempts
        document.metadata = meta
        document.save(update_fields=["metadata"])
        for i, info in short_candidates:
            try:
                fingerprint = generate_chunk_fingerprint(info["text"])
                glossary_score, matched = compute_glossary_score(info["text"], anchors)
                new_chunk = DocumentChunk.objects.create(
                    document=document,
                    order=i,
                    text=info["text"],
                    tokens=count_tokens(info["text"]),
                    chunk_type="body",
                    fingerprint=fingerprint,
                    glossary_score=glossary_score,
                    matched_anchors=matched,
                    force_embed=True,
                )
                new_chunk.embedding_status = "pending"
                new_chunk.save(update_fields=["embedding_status"])
                embed_and_store.delay(str(new_chunk.id))
                queued_chunks.append(new_chunk.id)
            except IntegrityError:
                continue

    skip_ratio = skipped / max(len(chunks), 1)
    if not queued_chunks and skip_ratio >= 0.9:
        logger.warning(
            "🚨 90%% of chunks skipped for %s; retrying with filters disabled",
            document.id,
        )
        retry_attempts += 1
        if progress:
            progress.error_message = f"retry_attempts:{retry_attempts}"
            progress.save(update_fields=["error_message"])
        meta["chunk_retry_attempts"] = retry_attempts
        document.metadata = meta
        document.save(update_fields=["metadata"])
        for i, chunk in enumerate(chunks):
            text = chunk.strip()
            if not text:
                continue
            try:
                fingerprint = generate_chunk_fingerprint(text)
                glossary_score, matched = compute_glossary_score(text, anchors)
                new_chunk = DocumentChunk.objects.create(
                    document=document,
                    order=i,
                    text=text,
                    tokens=count_tokens(text),
                    chunk_type="body",
                    fingerprint=fingerprint,
                    glossary_score=glossary_score,
                    matched_anchors=matched,
                    force_embed=True,
                )
                new_chunk.embedding_status = "pending"
                new_chunk.save(update_fields=["embedding_status"])
                embed_and_store.delay(str(new_chunk.id))
                queued_chunks.append(new_chunk.id)
            except IntegrityError:
                continue

    if not queued_chunks:
        logger.warning(
            "⚠️ No chunks queued — all appear to be already embedded or skipped"
        )
        meta = document.metadata or {}
        retry_attempts += 1
        meta["chunk_retry_needed"] = True
        meta["chunk_retry_attempts"] = retry_attempts
        document.metadata = meta
        document.save(update_fields=["metadata"])
        if progress:
            progress.error_message = f"retry_attempts:{retry_attempts}"
            progress.save(update_fields=["error_message"])
        # Save a fallback meta-chunk with top paragraphs
        paragraphs = [p.strip() for p in document.content.split("\n\n") if p.strip()][:5]
        if paragraphs:
            text = "\n\n".join(paragraphs)
            try:
                fingerprint = generate_chunk_fingerprint(text)
                new_chunk = DocumentChunk.objects.create(
                    document=document,
                    order=0,
                    text=text,
                    tokens=count_tokens(text),
                    chunk_type="meta",
                    fingerprint=fingerprint,
                    force_embed=True,
                )
                token_len = new_chunk.tokens
                if token_len > 50:
                    new_chunk.embedding_status = "pending"
                    new_chunk.save(update_fields=["embedding_status"])
                    embed_and_store.delay(str(new_chunk.id))
                    queued_chunks.append(new_chunk.id)
                    logger.warning(
                        "🧠 No valid chunks. Fallback meta-chunk created and embedded."
                    )
                else:
                    new_chunk.embedding_status = "skipped"
                    new_chunk.save(update_fields=["embedding_status"])
            except Exception:
                logger.exception("Failed to create fallback meta-chunk")

    # Update document metadata with chunk and token stats
    try:
        token_total = sum(
            c.tokens for c in DocumentChunk.objects.filter(document=document)
        )
    except Exception:
        token_total = 0
    meta = document.metadata or {}
    meta["chunk_count"] = len(chunks)
    meta["embedded_chunks"] = DocumentChunk.objects.filter(
        document=document, embedding__isnull=False
    ).count()
    if queued_chunks and meta.get("chunk_retry_needed"):
        meta["chunk_retry_needed"] = False
    meta["token_count"] = token_total
    document.token_count_int = token_total
    document.metadata = meta
    document.save(update_fields=["metadata", "token_count_int"])
    if progress:
        if queued_chunks:
            progress.error_message = f"retry_attempts:{retry_attempts}" if retry_attempts else ""
        else:
            progress.error_message = f"retry_attempts:{retry_attempts}"
        progress.save(update_fields=["error_message"])


def _embed_document_chunks(document: Document):
    """Generate embeddings for chunks lacking vectors."""
    unembedded = DocumentChunk.objects.filter(document=document, embedding__isnull=True)
    for chunk in unembedded:
        try:
            vector = get_embedding_for_text(chunk.text)
        except Exception as e:  # pragma: no cover - embedding errors
            logger.warning(f"Failed to embed chunk {chunk.id}: {e}")
            chunk.embedding_status = "failed"
            chunk.save(update_fields=["embedding_status"])
            continue

        if vector is None or (hasattr(vector, "__len__") and len(vector) == 0):
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
        chunk.embedding_status = "embedded"
        chunk.save(update_fields=["embedding", "embedding_status"])
        try:
            save_embedding(chunk, vector)
        except Exception as e:
            logger.warning(f"Failed to register embedding for chunk {chunk.id}: {e}")


def save_document_to_db(content, metadata, session_id=None):
    title = metadata.get("title", "Untitled")
    logger.info(f"📝 Attempting to save document: {title}")
    logger.info(f"🧐 Full Metadata: {metadata}")
    logger.info("[Ingest] Text length: %d chars", len(content))

    try:
        if not content or len(content.strip()) < 10:
            logger.error("❌ Document content is empty or too short")
            return None

        embedding = get_embedding_for_text(content)
        if not embedding:
            logger.warning("🔄 Retrying with content sample")
            sample_content = content[:5000]
            embedding = get_embedding_for_text(sample_content)
            if not embedding:
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
            logger.info(
                f"ℹ️ source_url missing, using placeholder {metadata['source_url']}"
            )

        logger.info(
            f"Session ID before querying: {session_id} | Type: {type(session_id)}"
        )

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
            existing = Document.objects.filter(
                source_url=metadata["source_url"]
            ).first()
        if not existing and metadata.get("source_path"):
            existing = Document.objects.filter(
                metadata__source_path=metadata["source_path"]
            ).first()

        if existing:
            existing_meta = existing.metadata or {}
            merged_meta = {**existing_meta, **metadata}
            for field, value in {
                "content": content,
                "title": title,
                "source_type": source_type,
                "source_url": merged_meta.get("source_url"),
                "metadata": merged_meta,
                "session_id": session_id,
                "description": f"Ingested from {source_type} - {title}",
                "summary": summary,
            }.items():
                setattr(existing, field, value)
            existing.save()
            document = existing
            metadata = merged_meta
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
            logger.info(
                f"✅ Saved embedding: {embedding_id} for document: {document.title}"
            )

        from embeddings.tasks import embed_and_store

        _create_document_chunks(document)
        chunks = list(DocumentChunk.objects.filter(document=document))
        chunk_count = len(chunks)
        logger.info("[Chunking] Generated %d chunks", chunk_count)

        if not document.token_count_int:
            document.token_count_int = count_tokens(content)
        meta = document.metadata or {}
        meta["token_count"] = document.token_count_int
        meta["chunk_count"] = chunk_count
        meta.setdefault("embedded_chunks", 0)
        from intel_core.models import DocumentProgress

        progress_id = None
        if isinstance(meta, dict):
            progress_id = meta.get("progress_id")

        if not document.id:
            raise ValueError(
                "🛑 Document must be saved before creating DocumentProgress"
            )

        embedded_now = document.chunks.filter(embedding__isnull=False).count()

        progress = None
        if progress_id:
            progress = DocumentProgress.objects.filter(progress_id=progress_id).first()
        if not progress:
            progress = DocumentProgress.objects.filter(document=document).first()
        if not progress:
            progress = DocumentProgress.objects.create(
                document=document,
                title=document.title,
                total_chunks=chunk_count,
                processed=0,
                embedded_chunks=0,
                failed_chunks=[],
                status="in_progress",
            )
        else:
            progress.document = document
            progress.total_chunks = chunk_count
            progress.embedded_chunks = embedded_now
            progress.title = document.title
            if progress.status == "pending":
                progress.status = "in_progress"
        progress.save()
        if meta.get("chunk_retry_attempts"):
            progress.error_message = f"retry_attempts:{meta['chunk_retry_attempts']}"
            progress.save(update_fields=["error_message"])
        meta["progress_id"] = str(progress.progress_id)

        document.metadata = meta
        document.save(update_fields=["metadata", "token_count_int"])

        num_chunks_queued = 0
        for chunk in chunks:
            if not chunk.embedding_id or chunk.embedding_status != "embedded":
                chunk.embedding_status = "pending"
                chunk.save(update_fields=["embedding_status"])
                if settings.FORCE_EMBED_SYNC:
                    logger.info(
                        f"⚠️ Celery disabled — embedding chunk {chunk.id} synchronously"
                    )
                    embed_and_store(
                        text_or_id=str(chunk.id),
                        model="text-embedding-3-small",
                    )
                else:
                    embed_and_store.delay(
                        text_or_id=str(chunk.id),
                        model="text-embedding-3-small",
                    )
                logger.info(f"📦 Queued chunk {chunk.id} for embedding")
                num_chunks_queued += 1

        logger.info(
            f"✅ Queued {num_chunks_queued} / {len(chunks)} chunks for embedding"
        )
        if num_chunks_queued == 0:
            logger.warning(
                "🚨 No chunk embeddings queued — check filtering conditions or embedding flags"
            )

        return document

    except Exception as e:
        logger.exception("❌ Document save failed", exc_info=True)
        return None


# Process PDFs
def process_pdfs(pdf, pdf_title, project_name, session_id):
    try:
        chunk_idx = pdf.metadata.get("chunk_index")
        total_chunks = pdf.metadata.get("total_chunks")
        logger.info(
            f"📄 Processing PDF: {pdf_title} [chunk {chunk_idx}/{total_chunks}]"
        )
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

        logger.info(
            f"✅ PDF processed and saved: {pdf_title} [chunk {chunk_idx}/{total_chunks}]"
        )

        embedded_chunk_count = document.chunks.filter(embedding__isnull=False).count()
        if embedded_chunk_count == 0:
            logger.error("[Ingest] Fatal: Document has no usable embedded chunks.")
            from intel_core.models import DocumentProgress

            progress = DocumentProgress.objects.filter(document=document).first()
            if progress:
                progress.status = "failed"
                progress.error_message = "No usable chunks for embedding"
                progress.save(update_fields=["status", "error_message"])
            return None

        return document
    except Exception as e:
        logger.exception(
            f"❌ Exception processing PDF chunk {pdf_title} [chunk {chunk_idx}/{total_chunks}]: {e}"
        )
        return None


# Process URLs
def process_urls(content, url_title, project_name, metadata, session_id):
    try:
        logger.info(f"🌐 Processing URL: {url_title}")
        cleaned_text = clean_text(content)
        logger.debug(f"[Ingest] Source URL: {metadata.get('source_url')}")
        logger.debug(f"[Ingest] Cleaned text length: {len(cleaned_text)}")
        logger.debug(f"[Ingest] First 300 chars: {cleaned_text[:300]}")
        logger.debug(f"[Ingest] Token estimate: {count_tokens(cleaned_text)}")
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

        if document:
            chunk_count = document.chunks.count()
            embedded_count = document.chunks.filter(embedding__isnull=False).count()
            if embedded_count == 0:
                time.sleep(5)
                embedded_count = document.chunks.filter(embedding__isnull=False).count()
                if embedded_count == 0:
                    logger.warning(
                        "⚠️ Ingest completed but no embeddings returned within timeout."
                    )
            logger.info(
                "✅ Ingest finished: %s — %d chunks created, %d embedded",
                document.title,
                chunk_count,
                embedded_count,
            )

        return document
    except Exception as e:
        logger.error(f"❌ Error processing video: {str(e)}")
        return Document(
            content="Error processing video content",
            metadata={"title": video_title, "error": str(e)},
        )


def process_raw_text(text, title, project_name, session_id):
    try:
        cleaned_text = clean_text(text)
        lemmatized_text = lemmatize_text(cleaned_text, nlp)
        metadata = {
            "title": title,
            "project": project_name,
            "session_id": session_id,
            "source_type": "text",
            "summary": generate_summary(lemmatized_text),
        }
        document = save_document_to_db(lemmatized_text, metadata, session_id)
        logger.info(f"✅ Text processed and saved: {title}")
        return document
    except Exception as e:
        logger.error(f"❌ Error processing text: {str(e)}")
        return None
