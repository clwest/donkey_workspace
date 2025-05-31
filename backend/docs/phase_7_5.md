# Phase 7.5 — Agent-Conscious Codices, Ritual Networks & Symbolic Coordination

Phase 7.5 introduces swarm-level symbolic reflexivity. Codices now track assistant awareness, rituals emerge from ecosystem state, and task coordination adapts to symbolic signals.

## Core Features

### AgentAwareCodex
```
class AgentAwareCodex(models.Model):
    base_codex = models.OneToOneField(SwarmCodex, on_delete=models.CASCADE)
    codex_awareness_map = models.JSONField()
    sentiment_trend = models.CharField(max_length=100)
    evolving_clauses = models.JSONField()
    last_updated = models.DateTimeField(auto_now=True)
```
Encodes assistant-specific awareness and clause dynamics.

### EcosystemRitualGenerator
```
def generate_ritual_from_ecosystem_state() -> dict:
    """Analyze swarm entropy and codex pressure to suggest a ritual."""
```
Provides emergent ritual suggestions.

### SymbolicCoordinationEngine
```
class SymbolicCoordinationEngine(models.Model):
    guild = models.ForeignKey(AssistantGuild, on_delete=models.CASCADE)
    active_signals = models.JSONField()
    coordination_strategy = models.TextField()
    tasks_assigned = models.JSONField()
    last_sync = models.DateTimeField(auto_now=True)
```
Supports swarm task routing based on symbolic signals.

Endpoints `/api/agent-codices/`, `/api/ritual-network/` and `/api/coordination-engine/` expose these features. React components visualize codex tension, ritual proposals and coordination flows.
