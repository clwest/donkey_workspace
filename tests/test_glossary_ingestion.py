import pytest
from unittest.mock import patch

from intel_core.models import Document, DocumentChunk
from intel_core.utils import processing

pytest.importorskip("django")

@patch("intel_core.utils.processing.embed_and_store.delay")
@patch("intel_core.utils.processing.generate_chunk_fingerprint", return_value="fp")
@patch("intel_core.utils.processing.clean_and_score_chunk", side_effect=lambda t, chunk_index=None: {"text": t, "score": 1.0, "keep": True})
@patch("intel_core.utils.processing.generate_chunks", return_value=["body text"])
@patch("intel_core.utils.processing.AcronymGlossaryService.extract", return_value={"MCP": "Model Context Protocol"})
def test_ingestion_links_anchor(mock_extract, mock_chunks, mock_clean, mock_fp, mock_embed, db):
    doc = Document.objects.create(title="T", content="body text")
    processing._create_document_chunks(doc)
    chunk = DocumentChunk.objects.first()
    assert chunk.is_glossary
    assert chunk.anchor and chunk.anchor.slug == "mcp"
