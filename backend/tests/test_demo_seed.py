import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django
django.setup()

from django.core.management import call_command
from assistants.models import Assistant

call_command("seed_demo_assistants")
required = ["prompt-pal", "reflection-sage", "memory-weaver"]
missing = [s for s in required if not Assistant.objects.filter(slug=s).exists()]
if missing:
    raise SystemExit(f"Missing demos: {missing}")
print("demo seed test passed")
