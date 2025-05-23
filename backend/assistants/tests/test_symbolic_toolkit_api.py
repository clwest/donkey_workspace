from assistants.tests import BaseAPITestCase
from assistants.models import Assistant


class SymbolicToolkitAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        self.assistant = Assistant.objects.create(name="Assist")

    def test_toolkit_create_and_fetch(self):
        url = "/api/v1/assistants/interface/tools/"
        payload = {
            "user_id": "u1",
            "ritual_macros": {"macro": "step"},
            "codex_shortcuts": {},
            "assistant_triggers": {},
        }
        resp = self.client.post(url, payload, format="json")
        assert resp.status_code == 201
        toolkit_id = resp.json()["id"]

        resp = self.client.get(url, {"user_id": "u1"})
        assert resp.status_code == 200
        assert resp.json()["id"] == toolkit_id

    def test_ritual_intuition_panel(self):
        resp = self.client.get("/api/v1/assistants/ritual/intuition/")
        assert resp.status_code == 200
        data = resp.json()
        assert "suggestion" in data

    def test_adaptation_layer_in_interface(self):
        url = f"/api/v1/assistants/{self.assistant.id}/interface/"
        resp = self.client.get(url)
        assert resp.status_code == 200
        data = resp.json()
        assert "adaptation_layer" in data
