import pytest

pytest.importorskip("django")

from django.test import Client
from django.contrib.auth import get_user_model
from pathlib import Path


def test_template_diff_endpoint():
    User = get_user_model()
    user = User.objects.create_user(username="tmp", password="pw")
    client = Client()
    client.force_login(user)
    path = Path(__file__).resolve()
    url = f"/api/dev/templates/{path}/diff/"
    resp = client.get(url)
    assert resp.status_code == 200
    data = resp.json()
    assert "diff" in data
