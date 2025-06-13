import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from assistants.tests import BaseAPITestCase
from assistants.models import Assistant
from assistants.models.reflection import AssistantReflectionLog
from assistants.models.reflection import ReflectionGroup
from intel_core.models import Document


class ReflectionGroupingTests(BaseAPITestCase):
    def setUp(self):
        self.authenticate()
        self.assistant = Assistant.objects.create(name="A", slug="a")
        self.doc = Document.objects.create(title="Doc", content="text")

    def test_grouped_reflections_endpoint(self):
        for i in range(3):
            AssistantReflectionLog.objects.create(
                assistant=self.assistant,
                document=self.doc,
                summary=f"r{i}",
                title="t",
                group_slug="grp",
            )
        summary_log = AssistantReflectionLog.objects.create(
            assistant=self.assistant,
            document=self.doc,
            summary="sum",
            title="t",
            group_slug="grp",
            is_summary=True,
        )
        url = f"/api/intel/documents/{self.doc.id}/reflections/?group=true"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()["groups"][0]
        self.assertEqual(data["slug"], "grp")
        self.assertEqual(len(data["items"]), 3)
        self.assertEqual(data["summary"], summary_log.summary)

    def test_summary_marked_flag(self):
        log = AssistantReflectionLog.objects.create(
            assistant=self.assistant,
            document=self.doc,
            summary="sum",
            title="t",
            is_summary=True,
        )
        self.assertTrue(log.is_summary)

    def test_recent_reflections_filtered(self):
        AssistantReflectionLog.objects.create(
            assistant=self.assistant,
            document=self.doc,
            summary="keep",
            title="t",
        )
        other = Assistant.objects.create(name="B", slug="b")
        AssistantReflectionLog.objects.create(
            assistant=other,
            document=self.doc,
            summary="other",
            title="t",
        )
        deleted = AssistantReflectionLog.objects.create(
            assistant=self.assistant,
            document=self.doc,
            summary="gone",
            title="t",
        )
        deleted.delete()

        url = f"/api/assistants/{self.assistant.slug}/recent-reflections/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["summary"], "keep")

    def test_group_assignment_and_summary(self):
        log = AssistantReflectionLog.objects.create(
            assistant=self.assistant,
            document=self.doc,
            summary="text",
            title="t",
        )
        group = ReflectionGroup.objects.create(
            assistant=self.assistant, slug="devdocs", title="DevDocs"
        )
        url = f"/api/reflection-log/{log.id}/assign-group/"
        resp = self.client.patch(url, {"group": group.slug}, format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["group"], group.slug)

        summary_url = "/api/assistants/reflections/groups/summarize/"
        resp = self.client.post(
            summary_url, {"slug": group.slug, "assistant": self.assistant.slug}
        )
        self.assertEqual(resp.status_code, 200)
        group.refresh_from_db()
        self.assertIn("1 reflections", group.summary)
