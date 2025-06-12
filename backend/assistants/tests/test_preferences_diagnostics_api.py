from assistants.tests import BaseAPITestCase
from assistants.models import Assistant
from memory.models import SymbolicMemoryAnchor
from intel_core.models import Document, DocumentChunk, EmbeddingMetadata


class PreferencesDiagnosticsAPITest(BaseAPITestCase):
    def setUp(self):
        self.user = self.authenticate()
        self.assistant = Assistant.objects.create(name="Pref", slug="pref")

    def test_preferences_get_and_patch(self):
        url = f"/api/assistants/{self.assistant.slug}/preferences/"
        resp = self.client.get(url)
        assert resp.status_code == 200
        data = resp.json()
        assert data["tone"] == "friendly"

        patch = {"tone": "formal", "planning_mode": "long_term", "custom_tags": ["x"]}
        resp = self.client.patch(url, patch, format="json")
        assert resp.status_code == 200
        data = resp.json()
        assert data["tone"] == "formal"
        assert data["planning_mode"] == "long_term"
        assert "x" in data["custom_tags"]

    def test_run_diagnostics(self):
        anchor = SymbolicMemoryAnchor.objects.create(slug="t1", label="Term")
        doc = Document.objects.create(title="D", content="c", source_url="http://x.com")
        chunk = DocumentChunk.objects.create(
            document=doc,
            order=0,
            text="Term content",
            tokens=5,
            fingerprint="f1",
            anchor=anchor,
            is_glossary=True,
            glossary_score=0.9,
        )
        emb = EmbeddingMetadata.objects.create(model_used="t", num_tokens=5, vector=[0.1])
        chunk.embedding = emb
        chunk.save()
        self.assistant.documents.add(doc)

        url = f"/api/assistants/{self.assistant.slug}/diagnostics/"
        resp = self.client.post(url)
        assert resp.status_code == 200
        data = resp.json()
        assert "results" in data
        assert data["tested"] >= 1
