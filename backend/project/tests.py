from django.test import TestCase
from django.contrib.auth import get_user_model

from .models import Project, ProjectTask
from .serializers import ProjectSerializer


class ProjectTaskStatsTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="user", password="pw")
        self.project = Project.objects.create(user=self.user, title="Stats")
        ProjectTask.objects.create(
            project=self.project, title="t1", content="c", status="todo"
        )
        ProjectTask.objects.create(
            project=self.project, title="t2", content="c", status="in_progress"
        )
        ProjectTask.objects.create(
            project=self.project, title="t3", content="c", status="done"
        )

    def test_task_helper_methods(self):
        self.assertEqual(self.project.get_open_tasks().count(), 2)
        self.assertEqual(self.project.get_completed_tasks().count(), 1)
        self.assertEqual(self.project.open_task_count(), 2)
        self.assertEqual(self.project.completed_task_count(), 1)
        self.assertEqual(self.project.completion_percent(), 33)

    def test_serializer_includes_stats(self):
        data = ProjectSerializer(self.project).data
        self.assertEqual(data["open_task_count"], 2)
        self.assertEqual(data["completed_task_count"], 1)
        self.assertEqual(data["completion_percent"], 33)
