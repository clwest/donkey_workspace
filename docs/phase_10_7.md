# Phase 10.7 — Assistant-Scripted Cinemyths, Purpose-Loop Cinematic Engines & User-Immersive Reflective Theater

Phase 10.7 brings MythOS into experiential performance. Assistants now write and direct cinemyths that can be looped for symbolic reflection and played back for users.

## Core Features

### CinemythStoryline
```python
class CinemythStoryline(models.Model):
    authored_by = models.ForeignKey(Assistant, on_delete=models.CASCADE)
    storyline_title = models.CharField(max_length=150)
    act_structure = models.JSONField()
    memory_sources = models.ManyToManyField(SwarmMemoryEntry)
    codex_alignment_vector = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
```
Encodes mythic plots written by assistants.

### PurposeLoopCinematicEngine
```python
class PurposeLoopCinematicEngine(models.Model):
    linked_storyline = models.ForeignKey(CinemythStoryline, on_delete=models.CASCADE)
    loop_condition = models.TextField()
    symbolic_entropy_threshold = models.FloatField()
    convergence_detected = models.BooleanField(default=False)
    completed_cycles = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
```
Loops cinemyths until a reflection goal is achieved.

### ReflectiveTheaterSession
```python
class ReflectiveTheaterSession(models.Model):
    viewer_identity = models.CharField(max_length=150)
    active_cinemyth = models.ForeignKey(CinemythStoryline, on_delete=models.CASCADE)
    codex_interaction_log = models.TextField()
    symbolic_mood_map = models.JSONField()
    reflection_rating = models.FloatField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
```
Logs user exposure to symbolic theater events.

## API Endpoints
- `/api/cinemyths/` — view and launch film arcs
- `/api/purpose-loops/` — configure replay logic
- `/api/theater-sessions/` — monitor user reflection

## React Components
- `CinemythComposer.jsx`
- `PurposeLoopPlayer.jsx`
- `ReflectiveTheaterStage.jsx`

## Testing Goals
- Storylines store act structures and codex vectors
- Loops mark convergence correctly
- Theater sessions persist viewer reflection data
