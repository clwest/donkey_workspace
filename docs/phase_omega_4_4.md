# Phase Ω.4.4 — Summon Feedback Loops, Assistant Reflection Merge & Prompt Replay Lab

Phase Ω.4.4 introduces symbolic feedback channels and reflection merging tools. Assistants can now ingest user tone feedback, combine past reflections into a single narrative insight, and rerun prompts with memory mutations for deeper codex alignment.

## Core Components
- **SummonFeedbackPanel** – UI panel for giving thumbs‑up/down tone feedback, tagging issues, and leaving ritual notes.
- **ReflectionMergeInterface** – edit merged reflections from multiple `AssistantThoughtLog` entries.
- **PromptReplayLab** – rerun prompts with memory mutations and compare codex resonance.

### SummonFeedbackPanel Model
```python
class AgentFeedbackLog(models.Model):
    assistant = models.ForeignKey(Assistant, on_delete=models.CASCADE)
    prompt_usage = models.ForeignKey(PromptUsageLog, on_delete=models.CASCADE)
    tone_score = models.IntegerField()
    feedback_tags = models.JSONField()
    ritual_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```
Stores feedback for assistant summon sessions and links to prompt usage.

### ReflectionMergeInterface Model
```python
class AssistantReflectionInsight(models.Model):
    assistant = models.ForeignKey(Assistant, on_delete=models.CASCADE)
    merged_insight = models.TextField()
    memory_tags = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
```
Represents merged narrative insight derived from past reflections.

### PromptReplayLab Model
```python
class PromptReplayMutation(models.Model):
    original_prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE)
    mutation_trace = models.JSONField()
    codex_resonance_before = models.FloatField()
    codex_resonance_after = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
```
Tracks prompt replays and codex resonance changes.

## View Routes
- `/assistants/:id/summon-feedback` – view + record feedback after summoning an assistant.
- `/assistants/:id/reflection-merge` – merge past reflections into narrative insight.
- `/prompts/:id/replay` – rerun prompts with memory mutations and inspect codex resonance shifts.

## Testing Goals
- Verify feedback logs save tone scores, tags, and notes correctly.
- Ensure merged reflections display and save to `AssistantReflectionInsight`.
- Confirm prompt replays capture resonance before and after mutation.

---
Prepares for Phase Ω.4.5 — Codex Contract Visualizer, Assistant Draft Tool & Swarm-Aligned Prompt Packager.
