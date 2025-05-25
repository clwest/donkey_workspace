import pytest

pytest.importorskip("django")

from django.test import Client
from assistants.models import Assistant


def test_deployment_narrative_api(db):
    client = Client()
    a = Assistant.objects.create(name="A")

    resp = client.post(
        "/api/deploy/narrative/",
        data={"assistant": a.id, "narrative": "first"},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["assistant"] == str(a.id)

    resp_get = client.get("/api/deploy/narrative/")
    assert resp_get.status_code == 200


def test_deployment_replay_api(db):
    client = Client()
    a = Assistant.objects.create(name="B")
    vector_id = 1
    resp = client.post(
        f"/api/deploy/replay/{vector_id}/",
        data={"assistant": a.id, "output": "ok"},
    )
    assert resp.status_code == 201
    resp_get = client.get(f"/api/deploy/replay/{vector_id}/")
    assert resp_get.status_code == 200


def test_deployment_feedback_api(db):
    client = Client()
    a = Assistant.objects.create(name="C")
    resp = client.post(
        "/api/deploy/feedback/",
        data={"assistant": a.id, "suggestion": "try"},
    )
    assert resp.status_code == 201
    resp_get = client.get("/api/deploy/feedback/")
    assert resp_get.status_code == 200
