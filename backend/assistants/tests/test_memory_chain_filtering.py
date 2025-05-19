import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from django.contrib.auth import get_user_model
from assistants.models import Assistant, AssistantProject, AssistantMemoryChain
from memory.models import MemoryEntry
from mcp_core.models import Tag
from assistants.utils.memory_filters import get_filtered_memories


class MemoryChainFilteringTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="t", password="pw")
        self.assistant = Assistant.objects.create(name="A", specialty="t")
        self.project = AssistantProject.objects.create(
            assistant=self.assistant, title="P", created_by=self.user
        )
        self.tag1 = Tag.objects.create(name="One", slug="one")
        self.tag2 = Tag.objects.create(name="Two", slug="two")
        self.m1 = MemoryEntry.objects.create(
            event="m1",
            assistant=self.assistant,
            related_project=self.project,
            type="chat",
        )
        self.m1.tags.add(self.tag1)
        self.m2 = MemoryEntry.objects.create(
            event="m2",
            assistant=self.assistant,
            related_project=self.project,
            type="thought",
        )
        self.m2.tags.add(self.tag1)
        self.m3 = MemoryEntry.objects.create(
            event="m3",
            assistant=self.assistant,
            related_project=self.project,
            type="thought",
        )
        self.m3.tags.add(self.tag2)
        self.chain = AssistantMemoryChain.objects.create(
            project=self.project, title="chain"
        )
        self.chain.memories.set([self.m1, self.m2, self.m3])
        self.chain.filter_tags.set([self.tag1])
        self.chain.exclude_types = ["chat"]
        self.chain.save()

    def test_get_filtered_memories(self):
        qs = get_filtered_memories(self.chain)
        self.assertEqual(list(qs), [self.m2])
