import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from datetime import datetime
from unittest.mock import patch
from agents.utils.seasonal import get_current_season


class SeasonHelperTest(TestCase):
    def test_summer(self):
        with patch("agents.utils.seasonal.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2024, 7, 1)
            mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw)
            self.assertEqual(get_current_season(), "summer")

    def test_winter(self):
        with patch("agents.utils.seasonal.datetime") as mock_dt:
            mock_dt.now.return_value = datetime(2024, 12, 1)
            mock_dt.side_effect = lambda *args, **kw: datetime(*args, **kw)
            self.assertEqual(get_current_season(), "winter")
