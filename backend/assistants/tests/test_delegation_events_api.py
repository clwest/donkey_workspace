
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from assistants.tests import BaseAPITestCase

from assistants.models import Assistant, DelegationEvent


class DelegationEventsAPITest(BaseAPITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="viewer", password="pw")
        self.client.force_authenticate(user=self.user)
        self.parent = Assistant.objects.create(name="Parent", specialty="root")
        self.child = Assistant.objects.create(name="Child", specialty="helper")
        for i in range(30):
            event = DelegationEvent.objects.create(
                parent_assistant=self.parent,
                child_assistant=self.child,
                reason=f"r{i}",
            )
            DelegationEvent.objects.filter(id=event.id).update(
                created_at=timezone.now() + timedelta(minutes=i)
            )

    def test_recent_delegation_events_endpoint(self):
        url = "/api/v1/assistants/delegation_events/recent/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 25)
        first_created = data[0]["created_at"]
        last_created = data[-1]["created_at"]
        self.assertGreater(first_created, last_created)
        expected_fields = {
            "parent",
            "child",
            "reason",
            "summary",
            "memory_id",
            "session_id",
            "created_at",
        }
        self.assertTrue(expected_fields.issubset(data[0].keys()))
