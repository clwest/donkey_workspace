# Phase X.4 — MythOS Project Composer, Multi-Agent Prompt Debugger & Ritual Fork Replay Engine

Phase X.4 brings full symbolic development tooling to MythOS. Users can scaffold entire assistant-driven projects, trace prompt execution across agents, and replay divergent ritual threads to explore symbolic what-ifs. This marks the beginning of myth-level devops.

## Core Components
- **MythOS Project Composer** – build projects, define milestones, assign rituals, and link codex goals in one view
- **Multi-Agent Prompt Debugger** – trace prompt lineage, codex influence, and role-aligned mutations across the swarm
- **Ritual Fork Replay Engine** – visually simulate divergent ritual threads and score symbolic outcomes

### MythOS Project Composer Models
```python
class AssistantProject(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class AssistantObjective(models.Model):
    project = models.ForeignKey(AssistantProject, on_delete=models.CASCADE)
    assigned_assistants = models.ManyToManyField(Assistant, blank=True)
    ritual_blueprint = models.ForeignKey(EncodedRitualBlueprint, null=True, blank=True, on_delete=models.SET_NULL)
    codex_goal = models.CharField(max_length=200, blank=True)
    milestone_due = models.DateField(null=True, blank=True)
```
Defines projects and objectives that link rituals, codex goals, and assigned assistants.

### Multi-Agent Prompt Debugger Models
```python
class PromptMutationTrace(models.Model):
    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE, related_name="mutation_traces")
    parent_prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE, related_name="children")
    codex_tag = models.CharField(max_length=150, blank=True)
    mutation_path = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
```
Logs prompt lineage and codex annotations for debugging across agents.

### Ritual Fork Replay Engine Models
```python
class RitualFork(models.Model):
    original_ritual = models.ForeignKey(EncodedRitualBlueprint, on_delete=models.CASCADE, related_name="forks")
    fork_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class RitualReplayState(models.Model):
    ritual_fork = models.ForeignKey(RitualFork, on_delete=models.CASCADE)
    belief_alignment_score = models.FloatField(null=True, blank=True)
    entropy_delta = models.FloatField(null=True, blank=True)
    codex_delta = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```
Stores fork metadata and replay scoring for symbolic comparisons.

## View Routes
- `/project/composer` – manage projects, assign assistants, and edit ritual milestones
- `/debug/prompts` – trace prompt → response timelines with codex annotations
- `/ritual/fork/replay` – replay ritual branches and merge or discard outcomes

## Testing Goals
- Validate projects and objectives save assistants, ritual blueprints, and codex goals
- Confirm prompt mutation traces link to parent prompts and codex tags
- Ensure ritual fork replays store alignment scores and entropy deltas

---
Prepares for Phase X.5 — Memory Shard Assembly Studio, Assistant Myth Audit Tools & Codex-Oriented Ritual Regression Inspector
