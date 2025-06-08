import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

import pytest
from io import StringIO
from django.core.management import call_command
from assistants.models import Assistant

pytest.importorskip("django")


@pytest.mark.django_db
def test_check_demo_seed_cli():
    Assistant.objects.filter(is_demo=True).delete()
    out = StringIO()
    call_command("check_demo_seed", stdout=out)
    text = out.getvalue()
    for slug in ["prompt-pal", "reflection-sage", "memory-weaver"]:
        assert slug in text
    assert Assistant.objects.filter(is_demo=True).count() >= 3
    for a in Assistant.objects.filter(is_demo=True):
        assert a.memories.count() > 0
