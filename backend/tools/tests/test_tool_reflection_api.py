import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
import django
django.setup()

from rest_framework.test import APITestCase
from unittest.mock import patch
from assistants.models import Assistant
from tools.models import Tool

class ToolReflectionAPITest(APITestCase):
    def setUp(self):
        self.tool = Tool.objects.create(name='Echo', slug='echo', module_path='x', function_name='f')
        self.assistant = Assistant.objects.create(name='A', slug='a')

    def test_list_endpoint(self):
        url = f'/api/tools/{self.tool.id}/reflections/'
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, 200)

    @patch('assistants.utils.assistant_reflection_engine.reflect_on_tool_usage', return_value=[])
    def test_reflect_endpoint(self, mock_reflect):
        url = f'/api/tools/{self.tool.id}/reflect/'
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, 200)
        mock_reflect.assert_called()
