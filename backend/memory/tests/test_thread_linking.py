import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from mcp_core.models import NarrativeThread
from memory.models import MemoryChain, MemoryEntry


class MemoryThreadLinkingTest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="t", password="pw")
        self.client.force_authenticate(user=self.user)
        self.thread = NarrativeThread.objects.create(title="T", created_by=self.user)
        self.chain1 = MemoryChain.objects.create(title="C1")
        self.chain2 = MemoryChain.objects.create(title="C2")
        self.m1 = MemoryEntry.objects.create(event="e1")
        self.m2 = MemoryEntry.objects.create(event="e2")
        self.chain1.memories.add(self.m1)
        self.chain2.memories.add(self.m2)

    def test_link_chain_endpoint(self):
        url = "/api/memory/threads/link_chain/"
        resp = self.client.post(url, {"chain_id": str(self.chain1.id), "thread_id": str(self.thread.id)}, format="json")
        assert resp.status_code == 200
        self.chain1.refresh_from_db()
        assert self.chain1.thread_id == self.thread.id

    def test_get_linked_chains_and_cross_recall(self):
        self.chain1.thread = self.thread
        self.chain2.thread = self.thread
        self.chain1.save()
        self.chain2.save()

        resp = self.client.get(f"/api/memory/threads/{self.thread.id}/linked_chains/")
        assert resp.status_code == 200
        assert len(resp.json()) == 2

        recall = self.client.get(f"/api/memory/chains/{self.chain1.id}/cross_project_recall/")
        ids = [m["id"] for m in recall.json()]
        assert str(self.m1.id) in ids
        assert str(self.m2.id) in ids
