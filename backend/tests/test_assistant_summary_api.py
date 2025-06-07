import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from assistants.tests import BaseAPITestCase
from assistants.models import Assistant, ChatSession, AssistantChatMessage, ChatIntentDriftLog
from assistants.models.reflection import AssistantReflectionLog
from memory.models import MemoryEntry, SymbolicMemoryAnchor
from intel_core.models import Document, DocumentChunk

class AssistantSummaryAPITest(BaseAPITestCase):
    def setUp(self):
        self.authenticate()

    def test_summary_endpoint(self):
        assistant = Assistant.objects.create(
            name="SumBot", specialty="demo", created_by=self.user, glossary_score=0.5
        )
        MemoryEntry.objects.create(assistant=assistant, event="m1")
        MemoryEntry.objects.create(assistant=assistant, event="m2")
        AssistantReflectionLog.objects.create(assistant=assistant, title="r", summary="s")
        anchor = SymbolicMemoryAnchor.objects.create(slug="a", label="A", memory_context=assistant.memory_context)
        doc = Document.objects.create(title="d", content="x")
        DocumentChunk.objects.create(document=doc, order=1, text="x", tokens=1, anchor=anchor, fingerprint="f1", is_drifting=True)
        anchor.reinforced_by.add(assistant)
        session = ChatSession.objects.create(assistant=assistant, session_id="s")
        msg = AssistantChatMessage.objects.create(session=session, role="user", content="hi")
        ChatIntentDriftLog.objects.create(assistant=assistant, session=session, user_message=msg, drift_score=0.6)
        assistant.skill_badges = ["alpha"]
        assistant.save()

        url = f"/api/assistants/{assistant.slug}/summary/"
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["memory_count"], 2)
        self.assertEqual(data["reflection_count"], 1)
        self.assertEqual(data["drifted_anchors"], 1)
        self.assertEqual(data["reinforced_anchors"], 1)
        self.assertEqual(data["badge_count"], 1)
        self.assertEqual(data["first_question_drift_count"], 1)
