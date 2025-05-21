import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

import threading
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.text import slugify
from project.models import Project


class ProjectSlugConcurrencyTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="slugger", password="pw")

    def create_project(self, title, slugs):
        p = Project.objects.create(user=self.user, title=title)
        slugs.append(p.slug)

    def test_unique_slugs_under_concurrent_creation(self):
        slugs = []
        threads = [
            threading.Thread(
                target=self.create_project, args=("Amazing Project", slugs)
            )
            for _ in range(3)
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.assertEqual(len(slugs), 3)
        self.assertEqual(len(slugs), len(set(slugs)))
        base = slugify("Amazing Project")[:40]
        expected = {base, f"{base}-1", f"{base}-2"}
        self.assertEqual(set(slugs), expected)
