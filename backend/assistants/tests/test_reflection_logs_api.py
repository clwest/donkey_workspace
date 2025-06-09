from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from assistants.tests import BaseAPITestCase

from assistants.models import Assistant, AssistantProject, AssistantReflectionLog


class AssistantReflectionLogAPITest(BaseAPITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="viewer", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="Tester", specialty="test")
        self.project = AssistantProject.objects.create(
            assistant=self.assistant, title="Proj", created_by=self.user
        )
        r1 = AssistantReflectionLog.objects.create(
            assistant=self.assistant,
            project=self.project,
            summary="first",
            title="R1",
        )
        r2 = AssistantReflectionLog.objects.create(
            assistant=self.assistant,
            project=self.project,
            summary="second",
            title="R2",
        )
        # ensure ordering
        AssistantReflectionLog.objects.filter(id=r1.id).update(
            created_at=timezone.now() - timedelta(minutes=1)
        )
        AssistantReflectionLog.objects.filter(id=r2.id).update(
            created_at=timezone.now()
        )
        self.ref1 = AssistantReflectionLog.objects.get(id=r1.id)
        self.ref2 = AssistantReflectionLog.objects.get(id=r2.id)

        # demo reflection
        self.assistant.is_demo = True
        self.assistant.save(update_fields=["is_demo"])
        self.demo_ref = AssistantReflectionLog.objects.create(
            assistant=self.assistant,
            summary="demo",
            title="Demo",
            demo_reflection=True,
        )

    def test_list_reflections_for_assistant(self):
        url = f"/api/v1/assistants/{self.assistant.slug}/reflections/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 2)
        self.assertGreater(data[0]["created_at"], data[1]["created_at"])
        expected = {"id", "created_at", "project", "summary", "linked_memory", "tags"}
        self.assertTrue(expected.issubset(set(data[0].keys())))

    def test_reflection_detail(self):
        url = f"/api/v1/assistants/reflections/{self.ref1.id}/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        expected = {
            "id",
            "summary",
            "raw_summary",
            "raw_prompt",
            "llm_summary",
            "linked_memory",
            "tags",
            "created_at",
        }
        self.assertTrue(expected.issubset(set(data.keys())))

    def test_patched_flag_in_list(self):
        self.ref1.insights = "Patched via Ω.9.52"
        self.ref1.save()
        url = f"/api/v1/assistants/{self.assistant.slug}/reflections/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        entry = next(x for x in data if x["id"] == str(self.ref1.id))
        self.assertTrue(entry["patched"])

    def test_detail_includes_replay_fields(self):
        from memory.models import ReflectionReplayLog

        replay = ReflectionReplayLog.objects.create(
            original_reflection=self.ref1,
            assistant=self.assistant,
            replayed_summary="better",
            reflection_score=0.7,
        )
        self.ref1.insights = "Patched via Ω.9.52"
        self.ref1.save()

        url = f"/api/v1/assistants/reflections/{self.ref1.id}/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertTrue(data["patched"])
        self.assertEqual(data["replayed_summary"], "better")
        self.assertEqual(data["reflection_score"], replay.reflection_score)

    def test_demo_reflection_filter(self):
        url = (
            f"/api/v1/assistants/{self.assistant.slug}/reflections/?demo_reflection=true"
        )
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        ids = [d["id"] for d in data]
        self.assertEqual(ids, [str(self.demo_ref.id)])
