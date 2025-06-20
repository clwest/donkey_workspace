
# Phase 15.4 — Guild Currency Exchange Hubs & Ritual Grant Systems

Phase 15.4 introduced MythOS's economic interface. Building on the funding protocols from Phase 15.3, assistants can now trade symbolic value, fund rituals and monitor guild reserves.

## Core Components
- **GuildCurrencyExchangeHub** – maintains exchange rates and reserves between guilds.
- **BeliefTokenMarket** – lists codex-linked tokens and tracks trade volume.
- **RitualGrantSystem** – assistants request grants and guild leaders approve funding.

### Frontend Interfaces
- `GuildExchangeDashboard.jsx` – view live exchange rates and recent trades.
- `TokenMarketPanel.jsx` – browse and trade belief tokens.
- `RitualGrantPortal.jsx` – submit and review ritual grant proposals.

### View Routes
- `/guilds/:id/exchange` – open exchange dashboard.
- `/market/tokens` – belief token market.
- `/ritual/grants` – grant submission and history.

### Testing Goals
- Exchange dashboard updates with each transaction.
- Token market lists correct tokens and logs volume.
- Grant portal flows from submission to outcome.

---
Phase 15.4 is complete. Next up is Phase 15.5 — Symbolic Forecast Indexes, Codex‑Weighted Trend Surfaces and Assistant Sentiment Modeling Engines.
=======
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


