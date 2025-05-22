
from django.contrib.auth import get_user_model
from assistants.tests import BaseAPITestCase
from assistants.models import Assistant, AssistantProject, AssistantHandoffLog


class AssistantHandoffLogAPITest(BaseAPITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="handofflog", password="pw")
        self.client.force_authenticate(user=self.user)
        self.a1 = Assistant.objects.create(name="Alpha", specialty="s1")
        self.a2 = Assistant.objects.create(name="Beta", specialty="s2")
        self.project = AssistantProject.objects.create(assistant=self.a1, title="P1")

    def test_create_and_list_handoff_log(self):
        url = "/api/v1/assistants/handoff-log/"
        resp = self.client.post(
            url,
            {
                "from": self.a1.slug,
                "to": self.a2.slug,
                "project": str(self.project.id),
                "summary": "passing baton",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(AssistantHandoffLog.objects.count(), 1)

        list_url = f"/api/v1/assistants/handoff-log/{self.a1.slug}/"
        resp2 = self.client.get(list_url)
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(len(resp2.json()), 1)
