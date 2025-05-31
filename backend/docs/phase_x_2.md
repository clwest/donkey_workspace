# Phase X.2 — Assistant Personality Deck Builder, Symbolic Feedback Tuner & Swarm-Linked Prompt Evolution Engine

Phase X.2 introduces symbolic customization and collaborative learning. Assistants gain persona decks crafted from card-based archetypes, structured feedback loops, and prompt mutation engines that sync across the swarm.

## Core Features
- **PersonalityDeck** – build persona decks using card types like role, tone, memory filter, and ritual disposition
- **SymbolicFeedbackRating** – rate ritual, memory, and codex decisions with codex clause links and memory actions
- **SwarmPromptEvolution** – track prompt mutation lineage and success metrics across assistants

### PersonalityDeck Models
```python
class PersonalityCard(models.Model):
    CARD_TYPES = [
        ("role", "Role"),
        ("tone", "Tone"),
        ("memory_filter", "Memory Filter"),
        ("ritual_disposition", "Ritual Disposition"),
    ]
    card_type = models.CharField(max_length=50, choices=CARD_TYPES)
    value = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class PersonalityDeck(models.Model):
    assistant = models.ForeignKey(Assistant, on_delete=models.CASCADE)
    cards = models.ManyToManyField(PersonalityCard, blank=True)
    deck_name = models.CharField(max_length=150)
    symbolic_override = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```
Build persona decks from archetypal cards and optionally export them as symbolic overrides.

### SymbolicFeedbackRating Model
```python
class SymbolicFeedbackRating(models.Model):
    assistant = models.ForeignKey(Assistant, on_delete=models.CASCADE)
    prompt_log = models.ForeignKey(PromptUsageLog, null=True, blank=True, on_delete=models.SET_NULL)
    agent_log = models.ForeignKey(AgentFeedbackLog, null=True, blank=True, on_delete=models.SET_NULL)
    memory_entry = models.ForeignKey(SwarmMemoryEntry, null=True, blank=True, on_delete=models.SET_NULL)
    rating = models.CharField(max_length=10)
    tag = models.CharField(max_length=100, blank=True)
    codex_clause = models.CharField(max_length=100, blank=True)
    memory_action = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```
Links user feedback to agent logs, prompt usage, and swarm memory for reflective tuning.

### SwarmPromptEvolution Model
```python
class SwarmPromptEvolution(models.Model):
    parent_prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE, related_name="evolutions")
    mutated_prompt_text = models.TextField()
    mutated_by = models.ManyToManyField(Assistant, blank=True)
    mutation_trace = models.JSONField()
    codex_link = models.ForeignKey(SwarmCodex, null=True, blank=True, on_delete=models.SET_NULL)
    success_score = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```
Tracks prompt mutations across assistants and codices with success metrics and trace data.

## View Routes
- `/assistants/:id/deck` — manage personality decks
- `/feedback/:assistantId` — record symbolic feedback
- `/codex/evolve` — inspect swarm prompt evolution

## Testing Goals
- Ensure personality decks store cards and link to assistants
- Validate feedback ratings connect to agent and prompt logs
- Confirm swarm prompt evolutions record mutation traces and codex links

---
Prepares for Phase X.3 — Swarm-Oriented Memory Composer, Dreamframe-Aware Belief Tuning Interface, & Auto-Ritualization Sandbox
