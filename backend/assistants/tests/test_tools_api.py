# flake8: noqa
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")

import django  # noqa: E402

django.setup()

from assistants.tests import BaseAPITestCase  # noqa: E402
from assistants.models import Assistant  # noqa: E402
from assistants.models.tooling import AssistantTool  # noqa: E402


class ToolsAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        self.assistant = Assistant.objects.create(name="A", specialty="t")
        self.tool = AssistantTool.objects.create(
            assistant=self.assistant,
            name="Tester",
            slug="tester",
        )

    def test_assign_and_list(self):
        url_assign = (
            f"/api/assistants/{self.assistant.slug}/tools/assign/"
        )
        resp = self.client.post(
            url_assign,
            {"tools": ["tester"]},
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        url_list = f"/api/assistants/{self.assistant.slug}/tools/"
        resp2 = self.client.get(url_list)
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(resp2.json()["tools"][0]["slug"], "tester")
