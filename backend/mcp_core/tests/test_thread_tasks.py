from django.test import TestCase
from django.contrib.auth import get_user_model

from mcp_core.models import NarrativeThread
from project.models import Project, ProjectMilestone
from mcp_core.tasks.thread_sync import update_thread_progress, sync_all_thread_progress

class ThreadProgressTaskTest(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="tuser")
        self.thread = NarrativeThread.objects.create(title="T")
        self.project = Project.objects.create(user=self.user, title="P", thread=self.thread)
        ProjectMilestone.objects.create(project=self.project, title="m1", status="Completed")
        ProjectMilestone.objects.create(project=self.project, title="m2", status="Planned")

    def test_update_thread_progress(self):
        update_thread_progress(self.thread.id)
        self.thread.refresh_from_db()
        self.assertEqual(self.thread.progress_percent, 50)
        self.assertEqual(self.thread.completion_status, NarrativeThread.CompletionStatus.IN_PROGRESS)

    def test_sync_all_thread_progress(self):
        result = sync_all_thread_progress()
        self.assertEqual(result, "done")
        self.thread.refresh_from_db()
        self.assertGreaterEqual(self.thread.progress_percent, 0)

