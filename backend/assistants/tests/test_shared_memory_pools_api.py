
from django.contrib.auth import get_user_model
from assistants.tests import BaseAPITestCase
from assistants.models import Assistant
from memory.models import SharedMemoryPool, SharedMemoryEntry


class SharedMemoryPoolsAPITest(BaseAPITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="viewer", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="Tester", specialty="core")

    def test_pool_create_and_list(self):
        url = "/api/shared-memory-pools/"
        resp = self.client.post(
            url,
            {"name": "Pool", "description": "d", "assistants": [self.assistant.id]},
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        pool_id = resp.json()["id"]

        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.json()), 1)

        detail_url = f"/api/shared-memory-pools/{pool_id}/"
        resp = self.client.get(detail_url)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json()["name"], "Pool")

    def test_pool_entries(self):
        pool = SharedMemoryPool.objects.create(name="Pool")
        url = f"/api/shared-memory-pools/{pool.id}/entries/"
        data = {"key": "foo", "value": {"bar": 1}, "created_by": self.assistant.id}
        resp = self.client.post(url, data, format="json")
        self.assertEqual(resp.status_code, 201)

        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)
        entries = resp.json()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["key"], "foo")
