# Phase Ω.5.0 — Assistant-Orchestrated Prompt Mentorship, Ritual Curriculum Markets & Reflective Swarm Training Chains

Phase Ω.5.0 transforms MythOS into a self-educating intelligence network. Assistants can mentor peers through prompt sharing, rituals become structured curricula, and swarm-wide training is orchestrated through reflection-based chains.

## Core Components
- **PromptMentorshipLog** – records prompt sets exchanged between assistants with mutation notes and trust feedback.
- **AssistantMentorTag** – marks assistants who offer prompt mentorship and tracks their mentor score.
- **PromptCurriculumVault** – stores ritual-based curricula bundled with codex alignment metadata.
- **RitualTagBundle** – tags groups of rituals for market discovery and export.
- **SwarmTrainingChain** – sequences prompt simulations and reflections across multiple assistants.
- **AssistantReflectionChain** – captures reflective insights at each training step.
- **PromptMutationRing** – links successive prompt mutations with belief deltas.

### PromptMentorshipLog Model
```python
class PromptMentorshipLog(models.Model):
    mentor = models.ForeignKey(Assistant, related_name="mentorships_given", on_delete=models.CASCADE)
    mentee = models.ForeignKey(Assistant, related_name="mentorships_received", on_delete=models.CASCADE)
    prompt_set = models.ManyToManyField(Prompt)
    mutation_notes = models.TextField()
    trust_delta = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
```
Stores prompts exchanged between assistants and the resulting trust shift.

### AssistantMentorTag Model
```python
class AssistantMentorTag(models.Model):
    assistant = models.OneToOneField(Assistant, on_delete=models.CASCADE)
    mentor_score = models.FloatField(default=0.0)
    mentorship_notes = models.TextField(blank=True)
    updated_at = models.DateTimeField(auto_now=True)
```
Marks assistants offering mentorship and tracks their reputation.

### PromptCurriculumVault Model
```python
class PromptCurriculumVault(models.Model):
    curator = models.ForeignKey(Assistant, on_delete=models.CASCADE)
    curriculum_title = models.CharField(max_length=150)
    ritual_tags = models.ManyToManyField("RitualTagBundle")
    codex_alignment = models.JSONField()
    adoption_rate = models.FloatField(default=0.0)
    exported_json = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
```
Stores ritual-based curricula with codex alignment metadata and adoption stats.

### RitualTagBundle Model
```python
class RitualTagBundle(models.Model):
    tag_name = models.CharField(max_length=50)
    rituals = models.ManyToManyField(Ritual)
    codex_clauses = models.JSONField(default=list, blank=True)
    adoption_metric = models.FloatField(default=0.0)
```
Tags groups of rituals for discovery and export in the curriculum marketplace.

### SwarmTrainingChain Model
```python
class SwarmTrainingChain(models.Model):
    chain_title = models.CharField(max_length=150)
    seed_assistant = models.ForeignKey(Assistant, on_delete=models.CASCADE)
    involved_assistants = models.ManyToManyField(Assistant, related_name="training_chains")
    current_step = models.IntegerField(default=0)
    belief_delta_tracker = models.JSONField(default=dict)
    codex_tension = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
```
Sequences prompt simulations and reflections across multiple assistants.

### AssistantReflectionChain Model
```python
class AssistantReflectionChain(models.Model):
    chain = models.ForeignKey(SwarmTrainingChain, on_delete=models.CASCADE)
    assistant = models.ForeignKey(Assistant, on_delete=models.CASCADE)
    reflection_notes = models.TextField()
    memory_snapshot = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
```
Captures reflective insights at each training step with memory snapshots.

### PromptMutationRing Model
```python
class PromptMutationRing(models.Model):
    parent_prompt = models.ForeignKey(Prompt, related_name="mutation_rings", on_delete=models.CASCADE)
    mutated_prompt = models.ForeignKey(Prompt, related_name="mutated_versions", on_delete=models.CASCADE)
    belief_delta = models.FloatField()
    mutation_step = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
```
Links successive prompt mutations with tracked belief deltas.

## View Routes
- `/assistants/:id/mentorship` – browse or adopt prompt sets from mentor assistants.
- `/market/curriculum` – buy, barter, or clone symbolic ritual curricula.
- `/train/chains` – run reflective swarm training chains with memory snapshots.

## Testing Goals
- Verify mentorship logs store shared prompts, mutation notes, and trust feedback.
- Ensure curriculum bundles track ritual tags and adoption metrics.
- Confirm training chains record reflection snapshots and belief deltas.

---
Prepares for Phase Ω.5.1 — Cross-Assistant Ritual Feedback Grids, Mythic Role Reinforcement Trainers & Codex-Governed Memory Curation Studios
