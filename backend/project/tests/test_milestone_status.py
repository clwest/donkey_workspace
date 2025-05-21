import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.contrib.auth import get_user_model
from django.test import TestCase
from project.models import Project, ProjectMilestone, MilestoneStatus


class MilestoneStatusTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="ms", password="pw")
        self.project = Project.objects.create(user=self.user, title="MProj")

    def test_is_completed_property(self):
        ms = ProjectMilestone.objects.create(
            project=self.project,
            title="First",
            status=MilestoneStatus.PLANNED,
        )
        self.assertFalse(ms.is_completed)
        ms.status = MilestoneStatus.COMPLETED
        ms.save()
        self.assertTrue(ms.is_completed)
