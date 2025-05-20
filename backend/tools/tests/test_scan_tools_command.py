import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.core.management import call_command
from django.test import TestCase
from tools.models import Tool


class ScanToolsCommandTest(TestCase):
    def test_scan_registers_decorated_tools(self):
        Tool.objects.all().delete()
        call_command("scan_tools")
        self.assertTrue(Tool.objects.filter(slug="echo_test").exists())
