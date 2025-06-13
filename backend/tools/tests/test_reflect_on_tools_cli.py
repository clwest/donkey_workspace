import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')
import django
django.setup()

from django.core.management import call_command
from unittest.mock import patch
from assistants.models import Assistant

@patch('assistants.utils.assistant_reflection_engine.reflect_on_tool_usage', return_value=[])
def test_reflect_on_tools_cli(mock_reflect, django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        a = Assistant.objects.create(name='A', slug='a')
        call_command('reflect_on_tools', '--assistant', a.slug)
        mock_reflect.assert_called_once_with(a)
