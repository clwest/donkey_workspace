import os
import importlib.util
import pytest

# Load chunking module directly (bypassing package imports) for isolated testing
chunk_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "document_services", "chunking.py")
)
spec = importlib.util.spec_from_file_location("chunking", chunk_path)
ck = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ck)


@pytest.fixture(autouse=True)
def fallback_nltk(monkeypatch):
    # Force fallback splitting (no NLTK available)
    monkeypatch.setattr(ck, "_has_nltk", False)


def test_split_text_empty_or_invalid():
    # Empty text or non-positive max_tokens returns empty list
    assert ck.split_text("", max_tokens=10) == []
    assert ck.split_text("Some text", max_tokens=0) == []


def test_split_text_single_chunk():
    text = "Hello world. This is a test! Yes?"
    # Large max_tokens should join all sentences
    chunks = ck.split_text(text, max_tokens=100)
    assert chunks == [text]


def test_split_text_multiple_sentence_chunks():
    text = "Hello world. Another sentence."
    # max_tokens small enough to force split at sentence boundaries
    chunks = ck.split_text(text, max_tokens=2)
    # Two sentences expected as separate chunks
    assert chunks == ["Hello world.", "Another sentence."]


def test_split_text_long_sentence_word_split():
    text = "a b c d e f"
    # Single long sentence split into word-based sub-chunks
    chunks = ck.split_text(text, max_tokens=2)
    assert chunks == ["a b", "c d", "e f"]


def test_fingerprint_consistency_and_uniqueness():
    # Same normalized text yields identical fingerprint
    f1 = ck.fingerprint("Test TEXT")
    f2 = ck.fingerprint(" test text ")
    assert f1 == f2
    # Different text yields different fingerprint
    f3 = ck.fingerprint("Different text")
    assert f1 != f3
    # Empty text yields empty fingerprint
    assert ck.fingerprint("") == ""


def test_summarize_chunks_no_truncate():
    # Short summary does not truncate
    chunks = ["one", "two", "three"]
    summary = ck.summarize_chunks(chunks)
    assert summary == "one two three"


def test_summarize_chunks_truncate(monkeypatch):
    # Force small MAX_SUMMARY_CHARS to test truncation
    monkeypatch.setattr(ck, "MAX_SUMMARY_CHARS", 10)
    chunks = ["one two", "three four"]
    summary = ck.summarize_chunks(chunks)
    # 'one two three four' truncated to <=10 chars -> 'one two...'
    assert summary == "one two..."
