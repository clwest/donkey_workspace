
from django.test import TestCase
from assistants.models import Assistant, AssistantProject, AssistantMemoryChain
from memory.models import MemoryEntry
from mcp_core.models import Tag
from assistants.utils.memory_filters import get_filtered_memories


class MemoryFilteringTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="FilterBot", specialty="filter")
        self.project = AssistantProject.objects.create(
            assistant=self.assistant, title="Proj"
        )
        self.chain = AssistantMemoryChain.objects.create(
            project=self.project, title="Main"
        )
        self.tag_keep = Tag.objects.create(name="keep", slug="keep")
        self.chain.filter_tags.add(self.tag_keep)

        m1 = MemoryEntry.objects.create(
            event="one", assistant=self.assistant, type="thought"
        )
        m2 = MemoryEntry.objects.create(
            event="two", assistant=self.assistant, type="note"
        )
        m2.tags.add(self.tag_keep)
        m3 = MemoryEntry.objects.create(
            event="three", assistant=self.assistant, type="chat"
        )
        self.chain.memories.set([m1, m2, m3])
        self.chain.exclude_types = ["thought", "chat"]
        self.chain.save()

    def test_get_filtered_memories(self):
        mems = list(get_filtered_memories(self.chain))
        self.assertEqual(len(mems), 1)
        self.assertEqual(mems[0].event, "two")
