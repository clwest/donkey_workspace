import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
import django
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from .models import NarrativeEvent


class NarrativeEventAPITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username='tester', password='pw')
        self.client.force_authenticate(user=self.user)

    def test_create_and_list_event(self):
        resp = self.client.post('/api/storyboard/', {'title': 'Scene 1', 'order': 1})
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(NarrativeEvent.objects.count(), 1)
        resp = self.client.get('/api/storyboard/')
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]['title'], 'Scene 1')

    def test_patch_event(self):
        ev = NarrativeEvent.objects.create(title='Old', order=1)
        url = f'/api/storyboard/{ev.id}/'
        resp = self.client.patch(url, {'title': 'New'}, format='json')
        self.assertEqual(resp.status_code, 200)
        ev.refresh_from_db()
        self.assertEqual(ev.title, 'New')
