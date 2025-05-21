import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from agents.models import GlobalMissionNode
from assistants.models import Assistant


class GlobalMissionNodeTest(TestCase):
    def setUp(self):
        self.a1 = Assistant.objects.create(name="A1", specialty="s")
        self.a2 = Assistant.objects.create(name="A2", specialty="s")

    def test_tree_creation(self):
        root = GlobalMissionNode.objects.create(title="Root", description="d")
        child = GlobalMissionNode.objects.create(
            title="Child", description="d", parent=root
        )
        root.assigned_assistants.add(self.a1)
        child.assigned_assistants.add(self.a2)
        self.assertEqual(child.parent, root)
        self.assertEqual(root.assigned_assistants.count(), 1)
