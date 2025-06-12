import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

import pytest
from assistants.models.assistant import Assistant, ChatSession
from intel_core.models import Document
from memory.models import MemoryEntry
from prompts.models import Prompt, PromptUsageTemplate

pytest.importorskip("django")

@pytest.mark.django_db
def test_reverse_accessors():
    assistant = Assistant.objects.create(name="A")
    project = None
    session = ChatSession.objects.create(session_id="1", assistant=assistant, project=project)
    assert session in assistant.chat_sessions.all()

    memory = MemoryEntry.objects.create(event="e", assistant=assistant, chat_session=session)
    assert memory in session.chat_entries.all()

    prompt = Prompt.objects.create(title="t", text="x")
    tmpl = PromptUsageTemplate.objects.create(title="u", prompt=prompt, agent=assistant, trigger_type="on_start")
    assert tmpl in prompt.usage_templates.all()

