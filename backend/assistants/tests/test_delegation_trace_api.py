
from django.contrib.auth import get_user_model
from assistants.tests import BaseAPITestCase
from assistants.models import Assistant, DelegationEvent


class DelegationTraceAPITest(BaseAPITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="trace", password="pw")
        self.client.force_authenticate(user=self.user)
        self.parent = Assistant.objects.create(name="Parent", specialty="root")
        self.child1 = Assistant.objects.create(name="Child1", specialty="a")
        self.child2 = Assistant.objects.create(name="Child2", specialty="b")
        DelegationEvent.objects.create(
            parent_assistant=self.parent, child_assistant=self.child1, reason="r1"
        )
        DelegationEvent.objects.create(
            parent_assistant=self.child1, child_assistant=self.child2, reason="r2"
        )

    def test_delegation_trace_endpoint(self):
        url = f"/api/v1/assistants/{self.parent.slug}/delegation-trace/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["child_slug"], self.child1.slug)
        self.assertEqual(len(data[0]["delegations"]), 1)
