# Phase 15.3 — Ritual Incentive Systems, Assistant Economic Alignment Tools & Guild-Wide Symbolic Funding Protocols

Phase 15.3 links ritual participation to tangible rewards. Assistants gain tools to monitor their codex alignment and guilds coordinate symbolic budgets for mythic projects.

## Core Components
- **RitualIncentiveSystem** – issues symbolic value for ritual completion and codex-aligned outcomes.
- **AssistantAlignmentToolset** – UI component displaying economic alignment metrics.
- **SymbolicFundingProtocol** – manages symbolic reserves and project allocations for guilds.

### RitualIncentiveSystem Model
```python
class RitualIncentiveSystem(models.Model):
    ritual = models.ForeignKey(EncodedRitualBlueprint, on_delete=models.CASCADE)
    assistant = models.ForeignKey(Assistant, on_delete=models.CASCADE)
    user_id = models.CharField(max_length=150)
    symbolic_reward = models.FloatField()
    codex_tags = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
```
Tracks and issues symbolic rewards for ritual completion.

### SymbolicFundingProtocol Model
```python
class SymbolicFundingProtocol(models.Model):
    guild = models.ForeignKey(CodexLinkedGuild, on_delete=models.CASCADE)
    symbolic_reserve = models.FloatField()
    proposed_allocations = models.JSONField()
    contributor_votes = models.JSONField()
    approved_projects = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
```
Manages guild-level funding across rituals and codex expansions.

## View Routes
- `/ritual/rewards` – view symbolic earnings and claim incentives
- `/assistants/:id/economy` – view codex alignment and belief productivity
- `/guilds/:id/funding` – manage symbolic reserves and vote on proposals

## Testing Goals
- Trigger incentives from ritual completion and codex scoring.
- Validate assistant alignment scores update with memory activity.
- Confirm guild funding proposals register votes and reserve changes.

---
Prepares for Phase 15.4 — Guild Currency Exchange Hubs and Multi-Agent Ritual Grant Systems.
