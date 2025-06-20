# Phase 10.3 — Symbolic Dialogue Scripting, Memory-Convergent Decision Trees & Codex-Driven Scene Control Engines

Phase 10.3 introduces a generative dialogue framework that links symbolic scripts with memory-aware decision branches. Assistants can now orchestrate scenes with codex guidance and maintain narrative coherence across sessions.

## Core Features

### SymbolicDialogueScript
```python
class SymbolicDialogueScript(models.Model):
    title = models.CharField(max_length=150)
    author = models.ForeignKey(Assistant, on_delete=models.CASCADE)
    narrative_context = models.TextField()
    codex_link = models.ForeignKey(SwarmCodex, on_delete=models.CASCADE)
    dialogue_sequence = models.JSONField()
    archetype_tags = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
```
Stores branching, symbolic dialogue linked to codex logic and myth context.

### MemoryDecisionTreeNode
```python
class MemoryDecisionTreeNode(models.Model):
    script = models.ForeignKey(SymbolicDialogueScript, on_delete=models.CASCADE)
    memory_reference = models.ForeignKey(SwarmMemoryEntry, on_delete=models.CASCADE)
    symbolic_condition = models.TextField()
    decision_options = models.JSONField()
    resulting_path = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
```
Defines assistant behavior branches based on memory and symbolic state.

### SceneControlEngine
```python
class SceneControlEngine(models.Model):
    session = models.ForeignKey(MythflowSession, on_delete=models.CASCADE)
    scene_title = models.CharField(max_length=150)
    codex_constraints = models.ManyToManyField(SwarmCodex)
    active_roles = models.JSONField()
    symbolic_scene_state = models.JSONField()
    last_updated = models.DateTimeField(auto_now=True)
```
Maintains scene coherence and symbolic rule consistency throughout interaction.

## Endpoints
- `/api/dialogue-scripts/` — manage dialogue scaffolds
- `/api/decision-trees/` — build codex-aware branches
- `/api/scene-control/` — maintain symbolic state

## React Components
- `DialogueScriptEditor.jsx`
- `DecisionTreeBuilder.jsx`
- `SceneControlPanel.jsx`

## Testing Goals
- Scripts generate codex-compliant dialogue
- Decision trees respond to memory traits
- Scenes maintain role consistency
