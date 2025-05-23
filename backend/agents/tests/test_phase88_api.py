import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from assistants.models import Assistant


class Phase88APITest(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(username="u88", password="pw")
        self.client.force_authenticate(user=self.user)
        self.assistant = Assistant.objects.create(name="A")

    def test_create_forecasting_ledger(self):
        resp = self.client.post(
            "/api/forecasting-ledgers/",
            {
                "market_scope": "guild",
                "forecast_topic": "event",
                "participant_predictions": {"a": 1},
                "outcome_window": "2025",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/forecasting-ledgers/")
        self.assertEqual(len(list_resp.json()), 1)

    def test_create_future_contract(self):
        resp = self.client.post(
            "/api/future-contracts/",
            {
                "title": "C",
                "future_event_description": "future",
                "value_basis": {},
                "staked_tokens": {},
                "initiator": self.assistant.id,
                "expiration_timestamp": timezone.now().isoformat(),
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/future-contracts/")
        self.assertEqual(len(list_resp.json()), 1)

    def test_create_cosmo_alignment(self):
        resp = self.client.post(
            "/api/cosmo-alignment/",
            {
                "mythic_zone": "zone",
                "economic_data": {},
                "symbolic_alignment_rating": 0.7,
                "predictive_summary": "sum",
            },
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        list_resp = self.client.get("/api/cosmo-alignment/")
        self.assertEqual(len(list_resp.json()), 1)
