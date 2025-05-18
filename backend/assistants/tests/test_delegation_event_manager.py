import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.test import TestCase
import uuid

from assistants.models import Assistant, ChatSession, DelegationEvent
from assistants.utils.delegation import spawn_delegated_assistant
from memory.models import MemoryEntry


class DelegationEventModelTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="delegator", password="pw")
        self.parent = Assistant.objects.create(
            name="Parent", specialty="root", created_by=self.user
        )
        self.session = ChatSession.objects.create(
            assistant=self.parent,
            session_id=uuid.uuid4(),
        )
        self.memory = MemoryEntry.objects.create(
            event="Testing", assistant=self.parent, chat_session=self.session
        )

    def test_delegation_event_created_by_spawn(self):
        child = spawn_delegated_assistant(
            self.session, name="Child", memory_entry=self.memory
        )
        event = DelegationEvent.objects.first()
        self.assertIsNotNone(event)
        self.assertEqual(event.parent_assistant, self.parent)
        self.assertEqual(event.child_assistant, child)
        self.assertEqual(event.triggering_session, self.session)
        self.assertEqual(event.triggering_memory, self.memory)

    def test_recent_delegation_events_returns_latest_ten(self):
        for i in range(12):
            child = Assistant.objects.create(name=f"Child {i}", specialty="helper")
            event = DelegationEvent.objects.create(
                parent_assistant=self.parent,
                child_assistant=child,
                reason="test",
            )
            # ensure ordering by spreading created_at
            DelegationEvent.objects.filter(id=event.id).update(
                created_at=timezone.now() + timedelta(minutes=i)
            )

        events = DelegationEvent.objects.recent_delegation_events()
        self.assertEqual(len(events), 10)
        latest_time = max(ev.created_at for ev in events)
        earliest_time = min(ev.created_at for ev in events)
        self.assertGreater(latest_time, earliest_time)
        ids = list(events.values_list("id", flat=True))
        all_events = list(
            DelegationEvent.objects.order_by("-created_at").values_list("id", flat=True)
        )
        self.assertEqual(ids, all_events[:10])
