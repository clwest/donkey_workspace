from django.db import models

from assistants.models.assistant import Assistant
from agents.models.core import AgentFeedbackLog
from mcp_core.models import PromptUsageLog
from agents.models.lore import SwarmMemoryEntry, SwarmCodex
from prompts.models import Prompt


class PersonalityCard(models.Model):
    """Individual personality trait card for an assistant persona deck."""

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

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"{self.card_type}: {self.value}"


class PersonalityDeck(models.Model):
    """Collection of personality cards applied to an assistant."""

    assistant = models.ForeignKey(Assistant, on_delete=models.CASCADE)
    cards = models.ManyToManyField(PersonalityCard, blank=True)
    deck_name = models.CharField(max_length=150)
    symbolic_override = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return self.deck_name


class SymbolicFeedbackRating(models.Model):
    """User feedback tied to agents, prompts and swarm memory."""

    assistant = models.ForeignKey(Assistant, on_delete=models.CASCADE)
    prompt_log = models.ForeignKey(
        PromptUsageLog, null=True, blank=True, on_delete=models.SET_NULL
    )
    agent_log = models.ForeignKey(
        AgentFeedbackLog, null=True, blank=True, on_delete=models.SET_NULL
    )
    memory_entry = models.ForeignKey(
        SwarmMemoryEntry, null=True, blank=True, on_delete=models.SET_NULL
    )
    rating = models.CharField(max_length=10)
    tag = models.CharField(max_length=100, blank=True)
    codex_clause = models.CharField(max_length=100, blank=True)
    memory_action = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"Rating for {self.assistant.name}"


class SwarmPromptEvolution(models.Model):
    """Prompt mutation linked across assistants and codices."""

    parent_prompt = models.ForeignKey(
        Prompt, on_delete=models.CASCADE, related_name="evolutions"
    )
    mutated_prompt_text = models.TextField()
    mutated_by = models.ManyToManyField(Assistant, blank=True)
    mutation_trace = models.JSONField()
    codex_link = models.ForeignKey(
        SwarmCodex, null=True, blank=True, on_delete=models.SET_NULL
    )
    success_score = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"Evolution of {self.parent_prompt.slug}"
