import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import AssistantThoughtLog
from assistants.serializers import AssistantThoughtLogSerializer
from assistants.constants import THOUGHT_CATEGORY_CHOICES


class ThoughtCategoryChoicesTest(TestCase):
    def test_constant_synced(self):
        model_choices = AssistantThoughtLog._meta.get_field("category").choices
        serializer_choices = list(
            AssistantThoughtLogSerializer().fields["category"].choices.items()
        )
        self.assertEqual(model_choices, THOUGHT_CATEGORY_CHOICES)
        self.assertEqual(serializer_choices, THOUGHT_CATEGORY_CHOICES)

