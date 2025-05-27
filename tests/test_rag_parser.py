import pytest

from backend.pipelines import parse_rag_metadata


def test_parse_json_block():
    text = "Answer... [RAG]{\"used_chunk_ids\": [\"c1\", \"c2\"], \"match_score\": 0.9, \"rag_grounded\": true}[/RAG]"
    data = parse_rag_metadata(text)
    assert data["used_chunk_ids"] == ["c1", "c2"]
    assert data["match_score"] == 0.9
    assert data["rag_grounded"] is True


def test_parse_key_value_block():
    text = """Response text
RAG Metadata:
chunk_ids: id1, id2
match_score: 0.75
rag_grounded: false
"""
    data = parse_rag_metadata(text)
    assert data["chunk_ids"] == ["id1", "id2"]
    assert data["match_score"] == 0.75
    assert data["rag_grounded"] is False
