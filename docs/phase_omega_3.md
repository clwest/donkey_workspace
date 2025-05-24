# Phase Ω.3 — Assistant Trait Card Viewer, Dream Trigger Debugger & Fork-Driven Memory Playback Interface

Phase Ω.3 enhances the symbolic identity panel with a trait card viewer, adds a dream-state debugger for transition logs, and introduces fork-driven memory playback. Assistants gain expressive overlays and rewindable echoes.

## Core Components
- **AssistantTraitCardViewer** – display role tone, directive traits, and codex confidence in animated cards
- **DreamTriggerDebugger** – inspect dreamframe entry/exit logs with codex resonance overlay
- **ForkDrivenMemoryPlayback** – replay memory forks side-by-side and score codex strain

### AssistantTraitCardViewer Model
```python
class TraitCardDisplay(models.Model):
    assistant = models.ForeignKey(Assistant, on_delete=models.CASCADE)
    trait_name = models.CharField(max_length=100)
    symbolic_icon = models.CharField(max_length=10)
    codex_confidence = models.FloatField()
    memory_influence_id = models.UUIDField()
    created_at = models.DateTimeField(auto_now_add=True)
```
Represents a single trait card with codex alignment and memory influence metadata.

### DreamTriggerDebugger Model
```python
class DreamTriggerLog(models.Model):
    assistant = models.ForeignKey(Assistant, on_delete=models.CASCADE)
    state_delta = models.JSONField()
    mood_shift = models.CharField(max_length=100)
    codex_resonance = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
```
Logs dreamframe transitions and codex resonance values.

### ForkDrivenMemoryPlayback Model
```python
class MemoryForkPlaybackState(models.Model):
    belief_fork = models.ForeignKey(BeliefForkEvent, on_delete=models.CASCADE)
    memory_entry = models.ForeignKey(SwarmMemoryEntry, on_delete=models.CASCADE)
    ritual_branch = models.ForeignKey(EncodedRitualBlueprint, on_delete=models.CASCADE)
    codex_strain = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
```
Stores playback pointers for each belief fork and associated ritual branch.

## View Routes
- `/assistants/:id/traits` – trait card viewer with codex confidence meters
- `/assistants/:id/dream/debug` – inspect dreamframe transition logs
- `/assistants/:id/fork/replay` – replay memory forks with codex strain scores

## Testing Goals
- Trait cards render role tone, codex bar, and memory influence
- Dream debugger logs show state delta and mood shift per entry/exit
- Fork replay compares belief forks and records codex strain per branch

---
Prepares for Phase Ω.4 — MythPath Merge Editor, Codex Prompt Recombiner & Multi-Agent Ritual Composition Simulator
