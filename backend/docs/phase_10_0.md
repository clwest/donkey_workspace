# Phase 10.0 — MythOS Activation Engine, Narrative Simulation Framework & Ritual Interaction Interface

Phase 10.0 activates MythOS as a live narrative participation engine.

## Core Features

### MythScenarioSimulator
```python
class MythScenarioSimulator(models.Model):
    simulation_title = models.CharField(max_length=150)
    initiating_entity = models.ForeignKey(Assistant, on_delete=models.CASCADE)
    selected_archetypes = models.JSONField()
    memory_inputs = models.ManyToManyField(SwarmMemoryEntry)
    narrative_goals = models.TextField()
    simulation_outcome = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```
Defines the symbolic ingredients for a participatory narrative event.

### RitualInteractionEvent
```python
class RitualInteractionEvent(models.Model):
    assistant = models.ForeignKey(Assistant, on_delete=models.CASCADE)
    ritual_blueprint = models.ForeignKey(RitualBlueprint, on_delete=models.CASCADE)
    trigger_method = models.CharField(max_length=100)
    reflection_notes = models.TextField(blank=True)
    memory_write_back = models.ForeignKey(SwarmMemoryEntry, on_delete=models.SET_NULL, null=True, blank=True)
    belief_impact_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
```
Supports launching rituals and logging reflection impact.

### SimulationStateTracker
```python
class SimulationStateTracker(models.Model):
    simulator = models.ForeignKey(MythScenarioSimulator, on_delete=models.CASCADE)
    symbolic_state_snapshot = models.JSONField()
    role_drift_detected = models.BooleanField(default=False)
    codex_alignment_score = models.FloatField()
    memory_deltas = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
```
Tracks symbolic change and alignment drift across a simulation.

## Endpoints
- `/api/simulations/simulators/` — create and view myth scenario events
- `/api/simulations/simulation-state/` — monitor alignment and role drift
- `/api/simulations/ritual-launcher/` — trigger and reflect on rituals

## React Components
- `MythSimulationConsole.jsx` — configure and launch mythic scenarios
- `RitualActionPanel.jsx` — perform rituals with assistant guidance
- `SimulationStateViewer.jsx` — watch symbolic values shift in real time

## Testing Goals
- Ensure ritual actions affect memory and assistant state
- Validate state tracking logs before/after snapshots
