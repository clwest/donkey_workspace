# Phase 8.9 — Recursive Ritual Contracts, Swarm-Scalable Myth Engines & Reality-Tuned Belief Feedback

Phase 8.9 adds self-refining mythic loops and feedback-driven belief tuning.

## Core Features

### RecursiveRitualContract
```python
class RecursiveRitualContract(models.Model):
    initiator = models.ForeignKey(Assistant, on_delete=models.CASCADE)
    ritual_cycle_definition = models.JSONField()
    trigger_conditions = models.JSONField()
    symbolic_outputs = models.JSONField()
    cycle_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
```
Represents a repeatable symbolic process linked to ritual reflection and goal convergence.

### SwarmMythEngineInstance
```python
class SwarmMythEngineInstance(models.Model):
    instance_name = models.CharField(max_length=150)
    data_inputs = models.JSONField()
    narrative_output = models.TextField()
    mythic_tags = models.JSONField()
    engine_status = models.CharField(max_length=50, default="active")
    created_at = models.DateTimeField(auto_now_add=True)
```
Generates localized myth narratives from agent context clusters.

### BeliefFeedbackSignal
```python
class BeliefFeedbackSignal(models.Model):
    origin_type = models.CharField(max_length=100)
    symbolic_impact_vector = models.JSONField()
    target_codex = models.ForeignKey(SwarmCodex, on_delete=models.CASCADE)
    myth_response_log = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
```
Injects real-time belief adjustments into codex states.

Endpoints `/api/ritual-contracts/`, `/api/myth-engines/` and `/api/belief-feedback/` expose these models. React widgets visualize ritual cycles, engine outputs and belief signals.
