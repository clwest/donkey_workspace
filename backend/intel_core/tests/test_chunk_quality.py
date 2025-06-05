import sys
import types
from types import SimpleNamespace
from embeddings.document_services.chunking import clean_and_score_chunk
from intel_core.utils.processing import compute_glossary_score

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


class DummyTags:
    def __init__(self, slugs=None, names=None):
        self._map = {"slug": slugs or [], "name": names or []}

    def values_list(self, field, flat=True):
        return self._map.get(field, [])


class DummyAnchor(SimpleNamespace):
    def __init__(self, slug, label=None, tag_slugs=None, tag_names=None):
        super().__init__(slug=slug, label=label or slug)
        self.tags = DummyTags(tag_slugs, tag_names)


def test_glossary_score_clamped():
    anchors = [DummyAnchor(f"term{i}", f"Term{i}") for i in range(50)]
    anchors.append(DummyAnchor("openai", "OpenAI"))

    score, matched = compute_glossary_score("OpenAI announced something", anchors)

    assert matched == ["openai"]
    assert score >= 0.1
