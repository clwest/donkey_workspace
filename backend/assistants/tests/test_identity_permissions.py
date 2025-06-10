from assistants.tests import BaseAPITestCase
from assistants.models import Assistant

class DemoIdentityPermissionTest(BaseAPITestCase):
    def test_demo_identity_no_auth(self):
        assistant = Assistant.objects.create(
            name="DemoP",
            slug="demop",
            is_demo=True,
            specialty="x",
            avatar="http://example.com/avatar.png",
        )
        url = f"/api/assistants/{assistant.slug}/identity/"
        resp = self.client.get(url)
        assert resp.status_code == 200
        data = resp.json()
        assert data["display_name"] == assistant.name
        assert data["avatar"] == assistant.avatar
        assert "persona_name" in data
