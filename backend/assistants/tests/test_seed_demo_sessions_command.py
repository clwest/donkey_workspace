import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from django.core.management import call_command
from assistants.models.demo_usage import DemoSessionLog


def test_seed_demo_sessions_command():
    call_command("seed_demo_assistants")
    call_command("seed_demo_sessions")
    assert DemoSessionLog.objects.count() > 0
