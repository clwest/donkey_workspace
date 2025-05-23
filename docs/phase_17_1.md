# Phase 17.1 — Swarm-Linked Assistant Diplomacy Interfaces, Codex Convergence Ceremony Systems & Cross-Guild Mythic Arbitration Councils

Phase 17.1 formalizes diplomatic coordination and codex convergence across MythOS. Assistants gain symbolic diplomacy interfaces, codices unify through ceremonial convergence rituals, and guilds deliberate mythic conflict resolution in arbitration councils.

## Core Components

### AssistantDiplomacyInterface Model
```python
class AssistantDiplomacyInterface(models.Model):
    initiator = models.ForeignKey(Assistant, on_delete=models.CASCADE, related_name="diplomacy_initiator")
    target = models.ForeignKey(Assistant, on_delete=models.CASCADE, related_name="diplomacy_target")
    proposal_type = models.CharField(max_length=100)
    dialogue_log = models.TextField()
    diplomatic_outcome = models.TextField()
    symbolic_agreement_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
```
Enables belief-aligned diplomatic proposals between assistants.

### CodexConvergenceCeremony Model
```python
class CodexConvergenceCeremony(models.Model):
    converging_codices = models.ManyToManyField(SwarmCodex)
    ceremony_title = models.CharField(max_length=150)
    symbolic_thresholds = models.JSONField()
    ritual_chain = models.ManyToManyField(EncodedRitualBlueprint)
    merged_codex_output = models.ForeignKey(SwarmCodex, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```
Ritualized codex merging mechanism driven by convergence scores and assistant agreement.

### MythicArbitrationCouncil Model
```python
class MythicArbitrationCouncil(models.Model):
    council_title = models.CharField(max_length=150)
    member_guilds = models.ManyToManyField(CodexLinkedGuild)
    belief_dispute_summary = models.TextField()
    council_votes = models.JSONField()
    resolved_codex_adjustments = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
```
Facilitates multi-guild resolution of codex mutation disputes and myth narrative conflict.

## View Routes
- `/diplomacy/assistants` — launch and respond to assistant diplomatic proposals
- `/codex/converge` — perform codex merging ceremonies and ritual chaining
- `/guilds/council` — submit myth conflict and vote on codex policy resolution

## Testing Goals
- Validate diplomacy logs record assistant voice lines and outcomes
- Confirm codex convergence output is coherent and symbolically valid
- Ensure arbitration council decisions mutate codices and update guild weight

---
Prepares for Phase 17.2 — Codex Federation Architectures and Ritualized Treaty Frameworks.
