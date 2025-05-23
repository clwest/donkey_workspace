# Phase 10.2 — Simulated Mythflow Reflection Loops, Narrative Pressure Adaptation & Agent-Curated Symbolic Plotlines

Phase 10.2 deepens MythOS with recursive reflection and adaptive plot curation.

## Core Features

### MythflowReflectionLoop
```python
class MythflowReflectionLoop(models.Model):
    session = models.ForeignKey(MythflowSession, on_delete=models.CASCADE)
    triggered_by = models.CharField(max_length=100)
    involved_assistants = models.ManyToManyField(Assistant)
    loop_reflections = models.TextField()
    belief_realignment_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
```
Enables assistants to reflect mid-session when narrative pressure spikes.

### NarrativePressureSensor Utility
```python
def calculate_narrative_pressure(session_id: int) -> dict:
    # Entropy, unresolved archetypes, stagnation indicators → triggers reflection loop
```
Detects entropy and tension so mythflow can realign.

### AgentPlotlineCuration
```python
class AgentPlotlineCuration(models.Model):
    assistant = models.ForeignKey(Assistant, on_delete=models.CASCADE)
    curated_arc_title = models.CharField(max_length=150)
    associated_memories = models.ManyToManyField(SwarmMemoryEntry)
    narrative_branch_notes = models.TextField()
    symbolic_convergence_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
```
Allows assistants to store proposed narrative branches.

## Endpoints
- `/api/reflection-loops/` — log symbolic convergence and trigger cadence
- `/api/narrative-pressure/` — monitor entropy and role drift
- `/api/plotline-curation/` — store agent-driven narrative branches

## React Components
- `ReflectionLoopPanel.jsx`
- `NarrativePressureGauge.jsx`
- `PlotlineCurationConsole.jsx`

## Testing Goals
- Reflection loops save and link to sessions
- Pressure sensor returns entropy values
- Curated plotlines persist associated memories
