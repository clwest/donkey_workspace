import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from django.core.management import call_command
from assistants.models.reflection import AssistantReflectionLog


def test_seed_reflections_command():
    call_command("seed_demo_assistants")
    call_command("seed_reflections")
    assert AssistantReflectionLog.objects.filter(demo_reflection=True).exists()
