import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from project.models import Project, ProjectTask, ProjectMilestone


class ProjectTaskViewSetTest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="taskuser", password="pw")
        self.client.force_authenticate(user=self.user)
        self.project = Project.objects.create(user=self.user, title="Proj")

    def test_task_crud(self):
        url = f"/api/projects/{self.project.id}/tasks/"
        resp = self.client.post(
            url,
            {"title": "Task", "notes": "n", "status": "todo", "priority": 1},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        task_id = resp.json()["id"]
        self.assertEqual(ProjectTask.objects.filter(project=self.project).count(), 1)

        resp = self.client.patch(
            f"/api/projects/{self.project.id}/tasks/{task_id}/",
            {"title": "Updated"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(ProjectTask.objects.get(id=task_id).title, "Updated")

        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.json()), 1)

        resp = self.client.delete(
            f"/api/projects/{self.project.id}/tasks/{task_id}/"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ProjectTask.objects.count(), 0)


class ProjectMilestoneViewSetTest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="mileuser", password="pw")
        self.client.force_authenticate(user=self.user)
        self.project = Project.objects.create(user=self.user, title="ProjM")

    def test_milestone_crud(self):
        url = f"/api/projects/{self.project.id}/milestones/"
        resp = self.client.post(
            url,
            {"title": "M1", "description": "d", "due_date": "2025-01-01"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        milestone_id = resp.json()["id"]
        self.assertEqual(
            ProjectMilestone.objects.filter(project=self.project).count(), 1
        )

        resp = self.client.patch(
            f"/api/projects/{self.project.id}/milestones/{milestone_id}/",
            {"title": "M2"},
            format="json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(
            ProjectMilestone.objects.get(id=milestone_id).title, "M2"
        )

        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resp.json()), 1)

        resp = self.client.delete(
            f"/api/projects/{self.project.id}/milestones/{milestone_id}/"
        )
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(ProjectMilestone.objects.count(), 0)
