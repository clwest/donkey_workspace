import pytest

pytest.importorskip("django")

from django.test import Client
from assistants.models import Assistant


def test_deployment_standards_api(db):
    client = Client()
    assistant = Assistant.objects.create(name="A")

    resp = client.post(
        "/api/deploy/standards/",
        data={"assistant_slug": assistant.slug, "goal": "check env"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "result" in data and data["result"]

    resp_list = client.get("/api/deploy/standards/")
    assert resp_list.status_code == 200
