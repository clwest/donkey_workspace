
from django.test import TestCase
from assistants.models import Assistant


class AssistantSlugCollisionTest(TestCase):
    def test_duplicate_name_generates_unique_slug(self):
        a1 = Assistant.objects.create(name="Helper", specialty="test")
        a2 = Assistant.objects.create(name="Helper", specialty="test")
        self.assertEqual(a1.slug, "helper")
        self.assertEqual(a2.slug, "helper-1")
