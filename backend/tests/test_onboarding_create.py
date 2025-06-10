import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.test_settings")
import django
django.setup()

from django.test import TestCase
from rest_framework.test import APIClient

class AssistantCreateAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        from django.contrib.auth import get_user_model
        self.user = get_user_model().objects.create_user('u@test.com', 'pass')
        self.client.force_authenticate(self.user)

    def test_create_assistant(self):
        resp = self.client.post('/api/assistants/', {
            'name': 'Test Assistant',
            'specialty': 'testing'
        })
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data['name'], 'Test Assistant')
