# Phase 10.1 — Real-Time Mythflow Sessions, Assistant Roleplay Modules & Belief-Driven Dialogue Generation

Phase 10.1 expands the MythOS simulation layer with live interaction and persona-driven dialogue.

## Core Features

### MythflowSession
```python
class MythflowSession(models.Model):
    session_name = models.CharField(max_length=150)
    active_scenario = models.ForeignKey(MythScenarioSimulator, on_delete=models.CASCADE)
    participants = models.ManyToManyField(Assistant)
    memory_trace = models.ManyToManyField(SwarmMemoryEntry)
    live_codex_context = models.ManyToManyField(SwarmCodex)
    session_status = models.CharField(max_length=50, default="active")
    created_at = models.DateTimeField(auto_now_add=True)
```
Hosts real-time symbolic interaction aligned with archetype and memory context.

### SymbolicDialogueExchange
```python
class SymbolicDialogueExchange(models.Model):
    session = models.ForeignKey(MythflowSession, on_delete=models.CASCADE)
    sender = models.ForeignKey(Assistant, on_delete=models.CASCADE)
    message_content = models.TextField()
    symbolic_intent = models.JSONField()
    codex_alignment_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
```
Stores codex-filtered assistant speech.

### RoleplayPersonaModule
Front-end component mapping an assistant to its `SymbolicIdentityCard`, archetype tone and codex.

## Endpoints
- `/api/mythflow-sessions/` — manage live sessions
- `/api/dialogue-exchange/` — stream dialogue entries
- `/api/roleplay-module/` — fetch persona config

## React Components
- `MythflowSessionConsole.jsx`
- `PersonaStageRenderer.jsx`
- `DialogueExchangeStream.jsx`

## Testing Goals
- Sessions initialize with symbolic context and memory trace
- Persona UI shows belief and tone
- Dialogue logs include codex alignment values
