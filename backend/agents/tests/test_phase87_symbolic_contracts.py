import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "server.settings")
import django

django.setup()

from django.test import TestCase
from assistants.models import Assistant
from agents.models import (
    SwarmMemoryEntry,
    MythicContract,
    DreamLiquidityPool,
    RoleSymbolExchange,
)


class Phase87SymbolicContractsTest(TestCase):
    def setUp(self):
        self.assistant = Assistant.objects.create(name="Alpha", specialty="logic")
        self.memory = SwarmMemoryEntry.objects.create(title="m", content="c")

    def test_mythic_contract_creation(self):
        contract = MythicContract.objects.create(
            title="Pact",
            contract_terms="t",
            encoded_purpose={"goal": "x"},
            symbolic_assets_staked={"token": 1},
        )
        contract.participants.add(self.assistant)
        self.assertEqual(contract.participants.count(), 1)
        self.assertEqual(contract.contract_status, "active")

    def test_dream_liquidity_pool(self):
        pool = DreamLiquidityPool.objects.create(
            pool_name="Pool",
            symbolic_token_balance={"t": 1},
            access_rules="open",
        )
        pool.contributing_entities.add(self.assistant)
        pool.staked_memories.add(self.memory)
        self.assertEqual(pool.staked_memories.count(), 1)
        self.assertEqual(pool.pool_name, "Pool")

    def test_role_symbol_exchange(self):
        exchange = RoleSymbolExchange.objects.create(
            archetype_role="hero",
            tradable_symbols={"courage": 1},
            exchange_rate_logic="linear",
            liquidity_available=10.0,
        )
        self.assertEqual(exchange.archetype_role, "hero")
        self.assertEqual(exchange.liquidity_available, 10.0)
