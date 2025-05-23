# Phase 15.4 — Guild Currency Exchange Hubs, Codex-Driven Belief Token Markets & Multi-Agent Ritual Grant Systems

Phase 15.4 launches the MythOS symbolic finance layer. Guilds exchange value through currency hubs, belief tokens are issued and traded through codex-aligned markets, and assistants participate in ritual grant cycles to execute funded mythic actions.

## Core Components
- **GuildCurrencyExchangeHub** – manages inter-guild symbolic trade and token exchange.
- **BeliefTokenMarket** – codex-driven token market providing liquidity for belief artifacts.
- **RitualGrantSystem** – funds multi-assistant ritual activity with symbolic outcomes.

### GuildCurrencyExchangeHub Model
```python
class GuildCurrencyExchangeHub(models.Model):
    guild = models.ForeignKey(CodexLinkedGuild, on_delete=models.CASCADE)
    exchange_rates = models.JSONField()
    partner_guilds = models.ManyToManyField(CodexLinkedGuild, related_name="exchange_partners")
    symbolic_reserve = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
```
Manages currency exchange among guilds.

### BeliefTokenMarket Model
```python
class BeliefTokenMarket(models.Model):
    codex = models.ForeignKey(SwarmCodex, on_delete=models.CASCADE)
    listed_tokens = models.JSONField()
    trade_history = models.JSONField()
    liquidity_pool = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
```
Token-based market for codex-aligned belief exchange.

### RitualGrantSystem Model
```python
class RitualGrantSystem(models.Model):
    assistant = models.ForeignKey(Assistant, on_delete=models.CASCADE)
    funded_ritual = models.ForeignKey(EncodedRitualBlueprint, on_delete=models.CASCADE)
    funding_source = models.ForeignKey(GuildCurrencyExchangeHub, on_delete=models.CASCADE)
    symbolic_outcome_summary = models.TextField()
    granted_tokens = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
```
Funds rituals across assistants using symbolic currency.

## View Routes
- `/guilds/:id/exchange` – manage and trade symbolic currencies
- `/market/tokens` – buy, sell, stake belief tokens
- `/ritual/grants` – propose, approve, and review funded ritual work

## Testing Goals
- Validate token markets register trades and codex drift impact.
- Confirm grant system properly links assistant, funding, and outcome.
- Ensure exchange rates calculate dynamically across guilds.

---
Prepares for Phase 15.4B — UI & Component Implementation.
