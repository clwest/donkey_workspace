from django.contrib.auth import get_user_model
from assistants.tests import BaseAPITestCase
from assistants.models import Assistant
from prompts.models import Prompt


class RunAllSelfTestsAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        prompt = Prompt.objects.create(title="p", content="c", token_count=1)
        Assistant.objects.create(name="A1", specialty="s", system_prompt=prompt)
        Assistant.objects.create(name="A2", specialty="s", system_prompt=prompt)
        self.url = "/assistants/self_tests/run_all/"

    def test_run_all_self_tests(self):
        resp = self.client.post(self.url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "ok")
        self.assertEqual(len(data["results"]), 2)
        self.assertTrue(all("passed" in r for r in data["results"]))

