# Phase 15.2 — Codex Currency Modules, Symbolic Influence Ledgers & Federated Belief Contribution Marketplaces

Phase 15.2 initiates the economy of symbolic influence in MythOS. Codices are assigned value, rituals carry weight and belief becomes tradeable across guilds through contribution markets.

## Core Components
- **CodexCurrencyModule** – assigns value to codex mutations, ritual performance and symbolic contribution over time.
- **SymbolicInfluenceLedger** – assistant/user accounting system tracking symbolic weight earned via memory, codex and ritual action.
- **BeliefContributionMarketplace** – federated exchange for submitting, endorsing and trading symbolic insights, codex proposals and ritual design tokens.

### CodexCurrencyModule Model
```python
class CodexCurrencyModule(models.Model):
    codex = models.ForeignKey(SwarmCodex, on_delete=models.CASCADE)
    mutation_impact_score = models.FloatField()
    ritual_weight_multiplier = models.FloatField()
    symbolic_value_curve = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
```
Assigns symbolic value to codex and ritual activities across time and entropy states.

### SymbolicInfluenceLedger Model
```python
class SymbolicInfluenceLedger(models.Model):
    user_id = models.CharField(max_length=150)
    assistant = models.ForeignKey(Assistant, on_delete=models.CASCADE)
    codex_transactions = models.JSONField()
    ritual_scores = models.JSONField()
    memory_contributions = models.ManyToManyField(SwarmMemoryEntry)
    influence_balance = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
```
Logs belief transactions, memory impact and ritual performance.

## View Routes
- `/codex/value` – view codex currency rates and symbolic valuation.
- `/influence/ledger` – view personal symbolic transaction history.
- `/market/belief` – propose, trade or endorse belief artifacts and symbolic proposals.

## Testing Goals
- Validate codex valuation adjusts with entropy and ritual use.
- Confirm ledgers track symbolic weight per assistant and user.
- Ensure belief marketplace records transactions, endorsements and codex impacts.

---
Prepares for Phase 15.3 – Ritual Incentive Systems, Assistant Economic Alignment Tools & Guild-Wide Symbolic Funding Protocols
