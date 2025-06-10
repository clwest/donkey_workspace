import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APIClient
from assistants.models import Assistant

client = APIClient()

assistant = Assistant.objects.create(name="Demo", slug="demo", is_demo=True)
resp = client.get(f"/api/assistants/{assistant.slug}/identity/")
assert resp.status_code == 200
print("demo identity route passed")
