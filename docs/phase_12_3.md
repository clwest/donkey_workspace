# Phase 12.3 — Memory-Driven Belief Inheritance Trees, Ritual Response Archives & MythOS Journey Export Systems

Phase 12.3 transforms symbolic history into portable legacy. User journeys, rituals and codex interactions now generate inheritance trees, get logged in detailed ritual archives and can be exported as personal myth bundles.

## Core Components

### BeliefInheritanceTree
```python
class BeliefInheritanceTree(models.Model):
    user_id = models.CharField(max_length=150)
    assistant = models.ForeignKey(Assistant, on_delete=models.CASCADE)
    core_belief_nodes = models.JSONField()
    memory_links = models.ManyToManyField(SwarmMemoryEntry)
    symbolic_summary = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
```
Maps assistant-user memory links into a lineage style belief view.

### RitualResponseArchive
```python
class RitualResponseArchive(models.Model):
    ritual_blueprint = models.ForeignKey(EncodedRitualBlueprint, on_delete=models.CASCADE)
    assistant = models.ForeignKey(Assistant, on_delete=models.CASCADE)
    user_id = models.CharField(max_length=150)
    ritual_inputs = models.JSONField()
    output_summary = models.TextField()
    belief_state_shift = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
```
Captures ritual interactions, input parameters and resulting belief changes.

### MythJourneyExportPackage
Utility `generate_journey_export_package(assistant, user_id, export_format)` bundles identity cards, memory maps and ritual contracts into a downloadable archive.

## View Routes
- `/belief/tree` — view memory linked belief lineage
- `/ritual/archive` — browse ritual response logs
- `/journey/export` — export a myth journey snapshot

## Testing Goals
- Ensure inheritance trees attach memory links correctly
- Validate ritual archives capture inputs and outputs
- Confirm journey export produces a file with the expected data
