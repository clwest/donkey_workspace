# Phase 15.5 — Symbolic Forecast Indexes, Codex-Weighted Trend Surfaces & Assistant Sentiment Modeling Engines

Phase 15.5 introduces real-time forecasting and sentiment mapping for MythOS. It layers symbolic analytics over the existing codex tools so assistants can predict belief trends and visualize emotional state.

## Core Components
- **SymbolicForecastIndex** – synthesizes codex health, ritual load and memory entropy into belief forecast scores.
- **CodexTrendSurfaceVisualizer** – pulls from recurrence loops and forecast indexes to display codex momentum and ritual saturation.
- **AssistantSentimentModelEngine** – captures assistant emotional state via codex conflict, ritual activity and belief drift.

### SymbolicForecastIndex Model
```python
class SymbolicForecastIndex(models.Model):
    index_title = models.CharField(max_length=150)
    linked_codex = models.ForeignKey(SwarmCodex, on_delete=models.CASCADE)
    trend_components = models.JSONField()
    ritual_activity_factor = models.FloatField()
    memory_entropy_factor = models.FloatField()
    forecast_output = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
```
Combines codex, ritual and memory metrics to produce a forecast output.

### AssistantSentimentModelEngine Model
```python
class AssistantSentimentModelEngine(models.Model):
    assistant = models.ForeignKey(Assistant, on_delete=models.CASCADE)
    symbolic_affect_log = models.JSONField()
    codex_resonance_score = models.FloatField()
    entropy_weighted_emotion_vector = models.JSONField()
    narrative_drift_tag = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
```
Tracks assistant mood and resonance with ongoing belief structures.

## View Routes
- `/forecast/symbolic` – belief forecast dashboard (guild/global).
- `/codex/trends` – mutation drift and ritual saturation explorer.
- `/assistants/:id/sentiment` – symbolic mood and codex resonance model viewer.

## Testing Goals
- Validate forecast indexes pull from ritual, memory and codex data.
- Confirm trend surfaces adapt to codex shifts and ritual activity.
- Ensure assistant sentiment models update with narrative pressure and codex resonance.

---
Prepares for Phase 15.6 — MythOS Ritual Market Feeds, Multi-Agent Trend Reactivity Models & Symbolic Infrastructure Stability Graphs.
