import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from django.utils import timezone
from assistants.models import Assistant
from agents.models import (
    ForecastingMarketLedger,
    SymbolicFutureContract,
    CosmoEconomicAlignmentMap,
)


class Phase88ModelTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="A")

    def test_forecasting_market_ledger(self):
        ledger = ForecastingMarketLedger.objects.create(
            market_scope="guild",
            forecast_topic="event",
            participant_predictions={"a": 1},
            outcome_window="2025",
        )
        self.assertEqual(ledger.market_scope, "guild")
        self.assertIsNone(ledger.accuracy_score)

    def test_symbolic_future_contract(self):
        contract = SymbolicFutureContract.objects.create(
            title="C",
            future_event_description="future",
            value_basis={},
            staked_tokens={},
            initiator=self.assistant,
            expiration_timestamp=timezone.now(),
        )
        self.assertEqual(contract.initiator, self.assistant)
        self.assertFalse(contract.contract_fulfilled)

    def test_cosmo_alignment_map(self):
        mapping = CosmoEconomicAlignmentMap.objects.create(
            mythic_zone="zone",
            economic_data={},
            symbolic_alignment_rating=0.5,
            predictive_summary="sum",
        )
        self.assertEqual(mapping.mythic_zone, "zone")
        self.assertAlmostEqual(mapping.symbolic_alignment_rating, 0.5)
