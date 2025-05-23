from assistants.tests import BaseAPITestCase
from django.urls import reverse


class NewAssistantInterfaceAPITest(BaseAPITestCase):
    def test_new_interface_endpoint(self):
        url = "/api/v1/assistants/new/interface/"
        resp = self.client.get(url)
        assert resp.status_code == 200
        data = resp.json()
        assert "assistant" in data
        assert "active_playbook" in data
        assert "template" in data
