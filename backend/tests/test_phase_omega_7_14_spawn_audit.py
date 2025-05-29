import pytest

pytest.importorskip("django")

from assistants.models import Assistant
from prompts.models import Prompt
from prompts.utils.mutation import fork_assistant_from_prompt


def test_no_duplicate_assistants_created(db):
    p = Prompt.objects.create(title="p", content="c", source="test")
    a = Assistant.objects.create(name="Base", system_prompt=p)
    fork_assistant_from_prompt(a, "new", spawn_trigger="t1")
    fork_assistant_from_prompt(a, "new", spawn_trigger="t1")
    forks = Assistant.objects.filter(parent_assistant=a)
    assert forks.count() == 1


def test_fork_blocked_when_not_allowed(db):
    p = Prompt.objects.create(title="p2", content="c", source="test")
    a = Assistant.objects.create(name="Block", system_prompt=p)
    fork_assistant_from_prompt(a, "n", allow_fork=False)
    assert Assistant.objects.filter(parent_assistant=a).count() == 0


def test_spawn_trigger_tracked(db):
    p = Prompt.objects.create(title="p3", content="c", source="test")
    a = Assistant.objects.create(name="Trig", system_prompt=p)
    child = fork_assistant_from_prompt(a, "x", spawn_trigger="glossary_miss")
    assert child.spawned_by == "glossary_miss"
