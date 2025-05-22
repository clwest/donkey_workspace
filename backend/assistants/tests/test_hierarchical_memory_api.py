
from django.contrib.auth import get_user_model
from assistants.tests import BaseAPITestCase
from assistants.models import Assistant, DelegationEvent
from memory.models import MemoryEntry


class HierarchicalMemoryAPITest(BaseAPITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="hier", password="pw")
        self.client.force_authenticate(user=self.user)
        self.parent = Assistant.objects.create(name="Parent", specialty="root")
        self.child = Assistant.objects.create(name="Child", specialty="a", parent_assistant=self.parent)
        self.grand = Assistant.objects.create(name="Grand", specialty="b", parent_assistant=self.child)
        self.m_trigger = MemoryEntry.objects.create(event="trigger", assistant=self.parent)
        self.event1 = DelegationEvent.objects.create(parent_assistant=self.parent, child_assistant=self.child, reason="r1", triggering_memory=self.m_trigger)
        DelegationEvent.objects.create(parent_assistant=self.child, child_assistant=self.grand, reason="r2")
        MemoryEntry.objects.create(event="child mem", assistant=self.child)
        MemoryEntry.objects.create(event="grand mem", assistant=self.grand)

    def test_hierarchical_memory_endpoint(self):
        url = f"/api/assistants/{self.parent.slug}/hierarchical-memory/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 3)
        first = next(m for m in data if m["id"] == str(self.m_trigger.id))
        self.assertEqual(first["delegation_event_id"], str(self.event1.id))
        child_entry = next(m for m in data if m["assistant"] == "Child")
        self.assertTrue(child_entry["is_delegated"])
        self.assertEqual(child_entry["depth"], 1)
