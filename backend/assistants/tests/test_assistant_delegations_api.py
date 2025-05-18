import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from assistants.models import Assistant, DelegationEvent


class AssistantDelegationsAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="viewer", password="pw")
        self.client.force_authenticate(user=self.user)
        self.parent = Assistant.objects.create(name="Parent", specialty="root")
        self.child = Assistant.objects.create(name="Child", specialty="helper")
        self.other = Assistant.objects.create(name="Other", specialty="other")
        DelegationEvent.objects.create(parent_assistant=self.parent, child_assistant=self.child, reason="r1")
        DelegationEvent.objects.create(parent_assistant=self.other, child_assistant=self.parent, reason="r2")

    def test_delegations_for_assistant(self):
        url = f"/api/assistants/{self.parent.slug}/delegations/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 2)
        participants = {d["parent"] for d in data} | {d["child"] for d in data}
        self.assertIn(self.parent.name, participants)
