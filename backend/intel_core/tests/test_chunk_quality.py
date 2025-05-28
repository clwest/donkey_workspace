import sys
import types
from types import SimpleNamespace
from embeddings.document_services.chunking import clean_and_score_chunk

# Stub spacy to avoid heavy dependency
spacy_stub = types.ModuleType("spacy")
spacy_stub.load = lambda name: None
spacy_stub.blank = lambda name: SimpleNamespace(__call__=lambda text: SimpleNamespace(ents=[], __iter__=lambda: iter([])))
sys.modules.setdefault("spacy", spacy_stub)


def test_spammy_header_rejected():
    result = clean_and_score_chunk("Thanks for watching my channel!", chunk_index=2)
    assert result["keep"] is False


def test_real_paragraph_kept():
    text = "OpenAI released GPT-5 today. It improves reasoning dramatically!"
    result = clean_and_score_chunk(text, chunk_index=2)
    assert result["keep"] is True


def test_edge_case_short_stopwords():
    text = "the and a the or"
    result = clean_and_score_chunk(text, chunk_index=2)
    assert result["keep"] is False
