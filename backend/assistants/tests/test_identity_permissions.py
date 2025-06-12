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


class PrivateIdentityPermissionTest(BaseAPITestCase):
    def setUp(self):
        self.user = self.authenticate()
        self.assistant = Assistant.objects.create(
            name="PrivA",
            slug="priva",
            specialty="x",
            created_by=self.user,
        )
        self.url = f"/api/assistants/{self.assistant.slug}/identity/"

    def test_owner_can_access(self):
        resp = self.client.get(self.url)
        assert resp.status_code == 200

    def test_other_user_forbidden(self):
        from django.contrib.auth import get_user_model

        other = get_user_model().objects.create_user(
            username="other", password="pw"
        )
        self.client.force_authenticate(user=other)
        resp = self.client.get(self.url)
        assert resp.status_code == 403
