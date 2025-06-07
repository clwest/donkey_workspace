from assistants.tests import BaseAPITestCase
from assistants.models import Assistant


class DemoAssistantAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        Assistant.objects.create(name="Demo1", specialty="t", is_demo=True)
        Assistant.objects.create(name="Regular", specialty="x")
        self.url = "/api/v1/assistants/demos/"

    def test_list_demos(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Demo1")
