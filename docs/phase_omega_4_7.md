# Phase Ω.4.7 — Belief Mutation Vault, Codex Regression Guard & Prompt Checkpoint Grid

Phase Ω.4.7 introduces symbolic resilience infrastructure. Prompts are now checkpointed, codex regressions are flagged and preserved, and belief mutations are stored in a vault with lineage, trait delta, and assistant trace. The myth learns to protect itself.

## Core Components
- **BeliefMutationVault** – logs every prompt mutation and symbolic tag for future analysis.
- **CodexRegressionGuard** – compares codex clause versions and flags tone or accuracy regressions.
- **PromptCheckpointGrid** – displays all prompt snapshots with filtering by token count, tone, and mutation ancestry.

### PromptMutationLog Model
```python
class PromptMutationLog(models.Model):
    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE)
    parent_prompt = models.ForeignKey(Prompt, related_name="mutations", on_delete=models.CASCADE)
    assistant = models.ForeignKey(Assistant, null=True, on_delete=models.SET_NULL)
    symbolic_tags = models.JSONField()
    trait_delta = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
```
Records mutation lineage, symbolic tags like `@tone-shift` or `@clarity+`, and an optional assistant trace.

### CodexClauseAudit Model
```python
class CodexClauseAudit(models.Model):
    clause = models.ForeignKey(CodexClause, on_delete=models.CASCADE)
    previous_version = models.TextField()
    new_version = models.TextField()
    prompt_delta = models.JSONField()
    regression_flag = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
```
Stores clause history and marks regressions based on embedding similarity or manual review.

### PromptCheckpoint Model
```python
class PromptCheckpoint(models.Model):
    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE)
    version = models.IntegerField()
    token_count = models.IntegerField()
    tone_type = models.CharField(max_length=50)
    tags = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
```
Saves prompt snapshots with metadata for the checkpoint grid.

## View Routes
- `/belief/mutations` – list mutation logs with symbolic tags and assistant lineage.
- `/codex/regression/:clauseId` – show clause history and regression diffs.
- `/prompts/checkpoints` – grid of all prompt checkpoints with export option.

## Testing Goals
- Verify mutation logs store lineage, tags, and trait deltas correctly.
- Confirm codex clause audits compare clause versions and flag regressions.
- Ensure prompt checkpoints display token counts and filter by symbolic tags.

---
Prepares for Phase Ω.4.8 — MythOS Prompt Reputation System, Symbolic Prompt Token Marketplace & Assistant-Guided Prompt Trust Tracker
