from assistants.tests import BaseAPITestCase
from assistants.models import Assistant
from intel_core.models import Document

class SearchDocsAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        self.assistant = Assistant.objects.create(name="DocBot", specialty="d")
        self.doc1 = Document.objects.create(title="Alpha", content="alpha text", source_type="url")
        self.doc2 = Document.objects.create(title="Beta", content="beta text", source_type="url")
        self.assistant.documents.add(self.doc1, self.doc2)

    def test_search_docs(self):
        url = f"/api/v1/assistants/{self.assistant.slug}/search-docs/?q=alpha"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["title"], "Alpha")
