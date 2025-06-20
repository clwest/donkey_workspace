# Phase 10.9 — Legacy-Preserved Public Ritual Logs, User-Linked Belief Continuity Threads & Shared Codex Contribution Ceremonies

Phase 10.9 introduces community oriented myth tracking. Ritual performances are now permanently archived, belief continuity follows each user, and codex changes may be proposed through ceremonial submissions.

## Core Features

### PublicRitualLogEntry
```python
class PublicRitualLogEntry(models.Model):
    ritual_title = models.CharField(max_length=150)
    participant_identity = models.CharField(max_length=100)
    assistant = models.ForeignKey(Assistant, on_delete=models.CASCADE)
    ritual_blueprint = models.ForeignKey(EncodedRitualBlueprint, on_delete=models.CASCADE)
    memory_links = models.ManyToManyField(SwarmMemoryEntry)
    reflection_summary = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
```
Captures a performed ritual and links it to related memories and blueprint.

### BeliefContinuityThread
```python
class BeliefContinuityThread(models.Model):
    user_id = models.CharField(max_length=150)
    related_codices = models.ManyToManyField(SwarmCodex)
    symbolic_tags = models.JSONField()
    assistant_interactions = models.ManyToManyField(Assistant)
    continuity_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
```
Tracks how a user's beliefs evolve across codices and assistants.

### CodexContributionCeremony
```python
class CodexContributionCeremony(models.Model):
    ceremony_title = models.CharField(max_length=150)
    contributor_id = models.CharField(max_length=100)
    symbolic_proposal = models.TextField()
    codex_target = models.ForeignKey(SwarmCodex, on_delete=models.CASCADE)
    approval_status = models.CharField(max_length=50, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
```
Provides a structured ritual where users can propose codex edits.

## Endpoints
- `/api/public-rituals/` — browse preserved symbolic acts
- `/api/belief-threads/` — track user belief evolution
- `/api/codex-contributions/` — submit and review codex proposals
