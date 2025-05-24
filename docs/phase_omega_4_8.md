# Phase Ω.4.8 — Prompt Reputation, Symbolic Token Marketplace & Trust Tracking

Phase Ω.4.8 activates the belief economy around prompt usage. Prompts earn symbolic reputation, can be exchanged in a tokenized swarm marketplace, and are scored by assistants using trust metrics linked to codex contracts, ritual outcomes, and memory fidelity.

## Core Components
- **PromptReputationLedger** – aggregates usage feedback and ritual outcome scores to produce a trust metric.
- **SymbolicPromptTokenMarketplace** – buy, inject, fork and rate prompts using symbolic tokens.
- **AssistantTrustTracker** – keeps an evolving trust map of prompts based on resonance and codex alignment.
- **PromptMarketplaceVault** – stores traded prompt bundles and symbolic signatures.

### PromptReputationScore Model
```python
class PromptReputationScore(models.Model):
    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE)
    ritual_effectiveness = models.FloatField()
    assistant_approval = models.FloatField()
    user_rating_tags = models.JSONField()
    symbolic_tags = models.JSONField()
    trust_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
```
Records a prompt's reputation metrics and final trust score.

### PromptTokenListing Model
```python
class PromptTokenListing(models.Model):
    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE)
    token_cost = models.FloatField()
    symbolic_tag_weight = models.FloatField()
    swarm_adoption_score = models.FloatField()
    codex_usage_score = models.FloatField()
    listed_at = models.DateTimeField(auto_now_add=True)
```
Represents a prompt up for trade with cost and adoption scores.

### AssistantPromptTrustMap Model
```python
class AssistantPromptTrustMap(models.Model):
    assistant = models.ForeignKey(Assistant, on_delete=models.CASCADE)
    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE)
    resonance_score = models.FloatField()
    symbolic_compliance = models.FloatField()
    dreamframe_volatility = models.FloatField()
    mutation_bias = models.FloatField()
    updated_at = models.DateTimeField(auto_now=True)
```
Tracks how trustworthy a prompt is for a specific assistant.

### PromptMarketplaceVault Model
```python
class PromptMarketplaceVault(models.Model):
    owner_assistant = models.ForeignKey(Assistant, on_delete=models.CASCADE)
    prompt_set = models.ManyToManyField(Prompt)
    symbolic_signature = models.TextField()
    exported_json = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
```
Stores bundled prompts with symbolic signatures for trade or export.

## View Routes
- `/prompts/:id/reputation` – show reputation sources and trust score.
- `/market/prompts` – buy, inject, fork and rate prompt sets.
- `/assistants/:id/trust` – display an assistant's prompt trust matrix.

## Testing Goals
- Verify reputation scores save ritual effectiveness, approval and tags.
- Ensure token listings track cost and adoption metrics.
- Confirm assistant trust maps update resonance and compliance scores.

---
Prepares for Phase Ω.4.9 — Assistant Ritual Memory Trainer, Swarm-Optimized Prompt Curriculum Generator & Codex-Aware Instruction Seed Compiler.
