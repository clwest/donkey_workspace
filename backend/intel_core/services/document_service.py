import json
import os
import uuid
from typing import List, Optional

from assistants.models.assistant import Assistant, ChatSession
from django.conf import settings
from django.core.files.storage import default_storage
from intel_core.models import Document, DocumentSet
from intel_core.processors.pdf_loader import load_pdfs
from intel_core.processors.url_loader import load_urls
from intel_core.processors.video_loader import load_videos
from mcp_core.models import Tag
from project.models import Project


class DocumentService:
    """High level document ingestion operations."""

    NULL_UUID = "00000000-0000-0000-0000-000000000000"

    @classmethod
    def _ensure_session(
        cls,
        session_id: Optional[str],
        assistant: Optional[Assistant],
        project: Optional[Project],
    ) -> str:
        """Return a valid session id and create a chat session if needed."""
        if not session_id or session_id == cls.NULL_UUID:
            session_id = str(uuid.uuid4())
        if assistant or project:
            ChatSession.objects.create(
                session_id=session_id,
                assistant=assistant,
                project=project,
            )
        return session_id

    @classmethod
    def _link_assistant(cls, assistant: Optional[Assistant], documents: List[Document]):
        if assistant:
            for doc in documents:
                if isinstance(doc, Document):
                    doc.linked_assistants.add(assistant)

    @classmethod
    def ingest_youtube(
        cls,
        video_urls: List[str],
        title: Optional[str],
        project_name: str,
        session_id: Optional[str],
        assistant: Optional[Assistant],
        project: Optional[Project],
    ) -> List[Document]:
        session_id = cls._ensure_session(session_id, assistant, project)
        documents = load_videos(video_urls, title, project_name, session_id)
        cls._link_assistant(assistant, documents)
        return documents

    @classmethod
    def ingest_urls(
        cls,
        urls: List[str],
        title: Optional[str],
        project_name: str,
        session_id: Optional[str],
        tag_names: List[str],
        assistant: Optional[Assistant],
        project: Optional[Project],
    ) -> List[Document]:
        session_id = cls._ensure_session(session_id, assistant, project)
        tags = []
        for tag_name in tag_names:
            cleaned = str(tag_name).strip().lower()
            if cleaned:
                tag, _ = Tag.objects.get_or_create(name=cleaned)
                tags.append(tag)
        documents = load_urls(urls, title, project_name, session_id)
        for doc in documents:
            if isinstance(doc, Document):
                doc.tags.set(tags)
        cls._link_assistant(assistant, documents)
        return documents

    @classmethod
    def ingest_pdfs(
        cls,
        uploaded_files,
        title: Optional[str],
        project_name: str,
        session_id: Optional[str],
        assistant: Optional[Assistant],
        project: Optional[Project],
    ) -> List[Document]:
        session_id = cls._ensure_session(session_id, assistant, project)
        file_paths = []
        for f in uploaded_files:
            path = default_storage.save(f"temp/{f.name}", f)
            file_paths.append(os.path.join(settings.MEDIA_ROOT, path))
        documents = load_pdfs(file_paths, title, project_name, session_id)
        cls._link_assistant(assistant, documents)
        return documents

    @classmethod
    def ingest_text(
        cls,
        text: str,
        title: Optional[str],
        project_name: str,
        session_id: Optional[str],
        tag_names: Optional[List[str]],
        assistant: Optional[Assistant],
        project: Optional[Project],
    ) -> List[Document]:
        session_id = cls._ensure_session(session_id, assistant, project)
        from intel_core.utils.processing import process_raw_text

        document = process_raw_text(
            text, title or "Manual Upload", project_name, session_id
        )
        if document and tag_names:
            tags = []
            for name in tag_names:
                cleaned = str(name).strip().lower()
                if cleaned:
                    tag, _ = Tag.objects.get_or_create(name=cleaned)
                    tags.append(tag)
            document.tags.set(tags)
        if document:
            cls._link_assistant(assistant, [document])
            return [document]
        return []

    @classmethod
    def ingest(
        cls,
        *,
        source_type: str,
        urls: Optional[List[str]] = None,
        files=None,
        text: Optional[str] = None,
        title: Optional[str] = None,
        project_name: str = "General",
        session_id: Optional[str] = None,
        assistant_id: Optional[str] = None,
        project_id: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> List[Document]:
        assistant = (
            Assistant.objects.filter(id=assistant_id).first() if assistant_id else None
        )
        project = Project.objects.filter(id=project_id).first() if project_id else None
        tags = tags or []
        if source_type == "youtube":
            return cls.ingest_youtube(
                urls or [], title, project_name, session_id, assistant, project
            )
        if source_type == "url":
            return cls.ingest_urls(
                urls or [], title, project_name, session_id, tags, assistant, project
            )
        if source_type == "pdf":
            uploaded_files = files or []
            return cls.ingest_pdfs(
                uploaded_files, title, project_name, session_id, assistant, project
            )
        if source_type == "text":
            return cls.ingest_text(
                text or "", title, project_name, session_id, tags, assistant, project
            )
        raise ValueError("Invalid source_type")

    @classmethod
    def create_document_set(
        cls,
        *,
        title: str,
        urls: Optional[List[str]] = None,
        videos: Optional[List[str]] = None,
        files=None,
        tags: Optional[List[str]] = None,
        project_name: str = "General",
        session_id: Optional[str] = None,
        assistant_id: Optional[str] = None,
        project_id: Optional[str] = None,
    ) -> DocumentSet:
        """Ingest multiple sources and wrap into a DocumentSet."""
        urls = urls or []
        videos = videos or []
        files = files or []
        docs: list[Document] = []
        if urls:
            docs.extend(
                cls.ingest(
                    source_type="url",
                    urls=urls,
                    title=title,
                    project_name=project_name,
                    session_id=session_id,
                    assistant_id=assistant_id,
                    project_id=project_id,
                    tags=tags,
                )
            )
        if videos:
            docs.extend(
                cls.ingest(
                    source_type="youtube",
                    urls=videos,
                    title=title,
                    project_name=project_name,
                    session_id=session_id,
                    assistant_id=assistant_id,
                    project_id=project_id,
                )
            )
        if files:
            docs.extend(
                cls.ingest(
                    source_type="pdf",
                    files=files,
                    title=title,
                    project_name=project_name,
                    session_id=session_id,
                    assistant_id=assistant_id,
                    project_id=project_id,
                )
            )

        document_set = DocumentSet.objects.create(
            title=title,
        )
        document_set.documents.set([d for d in docs if isinstance(d, Document)])
        return document_set
