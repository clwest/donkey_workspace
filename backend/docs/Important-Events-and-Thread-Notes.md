# 🧠 Memory System: Temporal Event Types and Narrative Threading

This document captures the key concepts, event types, and design decisions related to building a narrative-aware assistant capable of linking sessions, tracking emotional milestones, and reconstructing its own thought journey.

---

## 🔥 High-Priority Temporal / Journey-Based Event Types

These should be flagged and saved for assistant reflection, dashboard analytics, and long-term narrative building:

### 🧠 Cognitive Milestones

- `insight`: Aha moments or breakthroughs
- `realization`: New awareness or reframing of an idea
- `question`: Complex or open-ended inquiry (esp. those that lead to forks)
- `decision`: Finalized choices after deliberation

### 💬 Emotional / Vulnerable Moments

- `confession`: User reveals internal conflict, doubt, or past mistakes
- `emotion`: High affect moments (joy, anxiety, nostalgia, etc.)
- `frustration`: "I'm about to give up" or "this is pointless" messages

### 🧭 Strategic Turning Points

- `pivot`: We changed direction on a feature or approach
- `priority_shift`: A new goal or motivation overtakes previous ones
- `naming`: A concept gets a name or identity (e.g. Prompt Engine, DonkGPT)

### ⏱️ Temporal Anchors

- `start`: First message in a new session or topic
- `callback`: Returning to a previous idea/thread after a delay
- `completion`: Finalization or launch of a feature/workflow

---

## 🧵 Narrative Threading (Long-Form Context Linking)

To combat lost ideas across sessions, we’ll introduce `NarrativeThread`:

```python
class NarrativeThread(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

### Thread Attachments:

- `AssistantThoughtLog.thread` (FK)
- `MemoryEntry.thread` (FK)
- Future: `Session.thread`, `Project.thread`, etc.

### Assistant Capabilities:

- Suggest new threads based on topic drift or semantic clustering
- Auto-tag thoughts to threads with similarity search
- Summarize entire threads into blog posts, changelogs, or assistant memory capsules

---

## ✅ Next Steps

- [ ] Create `NarrativeThread` model + admin
- [ ] Add `thread` FK to `MemoryEntry` and `AssistantThoughtLog`
- [ ] Build manual thread picker in frontend ThoughtCard/MemoryDetail
- [ ] Add thread summary serializer
- [ ] Optional: LLM-powered topic clustering and inference

---

This .md file can be safely tracked in Git and updated during future work sessions to serve as our memory core for the assistant’s narrative reasoning system.
