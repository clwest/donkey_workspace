from assistants.tests import BaseAPITestCase
from assistants.models import Assistant


class AssistantCreateAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        self.url = "/api/assistants/"

    def test_first_flag(self):
        resp = self.client.post(
            self.url, {"name": "A", "specialty": "x"}, format="json"
        )
        assert resp.status_code == 201
        data = resp.json()
        assert data["is_first"] is True
        resp2 = self.client.post(
            self.url, {"name": "B", "specialty": "y"}, format="json"
        )
        assert resp2.status_code == 201
        assert resp2.json()["is_first"] is False
