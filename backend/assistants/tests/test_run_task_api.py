from assistants.tests import BaseAPITestCase
from assistants.models import Assistant

class RunTaskAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        self.assistant = Assistant.objects.create(name="Runner", specialty="t")

    def test_run_task(self):
        url = f"/api/v1/assistants/{self.assistant.slug}/run-task/"
        resp = self.client.post(url, {"task": "test"})
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("result", data)
