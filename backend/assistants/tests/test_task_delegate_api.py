
from django.contrib.auth import get_user_model
from assistants.tests import BaseAPITestCase
from assistants.models import Assistant, TaskAssignment


class TaskDelegateAPITest(BaseAPITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="del", password="pw")
        self.client.force_authenticate(self.user)
        self.sender = Assistant.objects.create(name="Sender", specialty="x")
        self.target = Assistant.objects.create(name="Target", specialty="y")
        self.url = f"/api/v1/assistants/{self.sender.id}/delegate-task/"

    def test_delegate_creates_assignment(self):
        resp = self.client.post(
            self.url,
            {
                "task_description": "Do work",
                "target_assistant_id": str(self.target.id),
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        assignment_id = resp.json()["assignment_id"]
        self.assertTrue(TaskAssignment.objects.filter(id=assignment_id).exists())

    def test_badge_requirement_enforced(self):
        self.target.skill_badges = ["reflection_ready"]
        self.target.save(update_fields=["skill_badges"])
        resp = self.client.post(
            self.url,
            {
                "task_description": "Do work",
                "target_assistant_id": str(self.target.id),
                "required_badges": ["reflection_ready"],
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 200)
        resp = self.client.post(
            self.url,
            {
                "task_description": "Do other",
                "target_assistant_id": str(self.target.id),
                "required_badges": ["semantic_master"],
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 400)
