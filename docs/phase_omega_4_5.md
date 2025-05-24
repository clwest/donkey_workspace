# Phase Ω.4.5 — Codex Contract Visualizer, Assistant Draft Tool & Swarm-Aligned Prompt Packager

Phase Ω.4.5 empowers users to formalize and export symbolic agreements between prompts, codex clauses, and assistant behavior. It introduces the Codex Contract Visualizer, a Draft Tool to propose new assistants based on symbolic intent, and a Prompt Packager to group codex-aligned behaviors into swarm-distributable sets.

## Core Components
- **CodexContractVisualizer** – displays symbolic obligations, codex clause references, and role inheritance for prompts.
- **AssistantDraftTool** – allows drag-and-drop prompt clustering, tone settings, and codex contract selection when creating new assistants.
- **SwarmAlignedPromptPackager** – groups prompts by ritual type, tone, or codex tags for export and reuse across assistants.

### CodexContractVisualizer Model
```python
class CodexContract(models.Model):
    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE)
    codex_clauses = models.JSONField()
    symbolic_expectations = models.JSONField()
    inherited_roles = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
```
Records prompt obligations and links to codex clauses and inherited roles.

### AssistantDraftTool Model
```python
class AssistantDraft(models.Model):
    name = models.CharField(max_length=150)
    tone = models.CharField(max_length=50)
    codex_contract_type = models.CharField(max_length=50)
    prompt_cluster = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
```
Stores pending assistant configurations before deployment.

### SwarmAlignedPromptPackager Model
```python
class PromptPackage(models.Model):
    name = models.CharField(max_length=150)
    prompts = models.ManyToManyField(Prompt)
    tags = models.JSONField()
    exported = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
```
Bundles prompts with metadata for swarm distribution and reuse.

## View Routes
- `/codex/contracts/:promptId` – show contract card with obligations, clause lineage, and inheritance markers.
- `/assistants/draft` – build assistant profiles from prompt clusters and codex tags.
- `/prompts/package` – group prompts and export symbolic prompt sets.

## Testing Goals
- Display contract cards with codex clause lineage and symbolic expectations.
- Validate assistant drafts store prompt clusters and tone settings.
- Confirm prompt packages export and attach codex tags correctly.

---
Prepares for Phase Ω.4.6 — Belief Mutation Vault, Codex Regression Guard, & Memory-Critical Prompt Checkpoints.
