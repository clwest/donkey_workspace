import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

import pytest
from io import StringIO
from django.core.management import call_command
from assistants.models import Assistant
from assistants.models.profile import AssistantUserProfile
from memory.models import MemoryEntry
from assistants.models.reflection import AssistantReflectionLog
from mcp_core.models import NarrativeThread

pytest.importorskip("django")


@pytest.mark.django_db
def test_repair_assistants_boot():
    assistant = Assistant.objects.create(name="Debugger", specialty="sys")
    assistant.memory_context = None
    assistant.archetype = None
    assistant.slug = None
    assistant.save(update_fields=["memory_context", "archetype", "slug"])

    out = StringIO()
    call_command("repair_assistants_boot", stdout=out)
    text = out.getvalue()
    assert "Debugger" in text

    assistant.refresh_from_db()
    assert assistant.memory_context is not None
    assert assistant.archetype == "debugger"
    assert assistant.slug

    profile = AssistantUserProfile.objects.get(assistant=assistant)
    assert profile.world == "core"
    assert profile.archetype == "debugger"

    assert MemoryEntry.objects.filter(assistant=assistant, type="assistant_intro").exists()
    assert AssistantReflectionLog.objects.filter(assistant=assistant).exists()
    assert NarrativeThread.objects.exists()
