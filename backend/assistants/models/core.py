from django.db import models
import uuid


class DelegationEventManager(models.Manager):
    """Manager with helper for recent events."""

    def recent_delegation_events(self, limit: int = 10):
        return self.order_by("-created_at")[:limit]


from memory.models import MemoryEntry
from prompts.models import Prompt
from project.models import ProjectTask, ProjectMilestone
from agents.models import SwarmMemoryEntry, GlobalMissionNode
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.conf import settings
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.fields import ArrayField
from tools.models import Tool
from pgvector.django import VectorField
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from story.models import LoreEntry


class AssistantMythLayer(models.Model):
    """Mythic layer of lore attached to an assistant."""

    assistant = models.ForeignKey(
        "assistants.Assistant", on_delete=models.CASCADE, related_name="myth_layers"
    )
    origin_story = models.TextField(blank=True)
    legendary_traits = models.JSONField(default=dict, blank=True)
    summary = models.TextField(blank=True)
    archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-last_updated"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return f"MythLayer for {self.assistant.name}"


# Used for structured memory and assistant sessions

# --- Choice Constants ---
THOUGHT_TYPES = [
    ("user", "User Input"),
    ("cot", "Chain of Thought"),
    ("generated", "Generated Thought"),
    ("planning", "Planning Step"),
    ("reflection", "Reflection"),
    ("mutation", "Mutation"),
    ("self_doubt", "Self Doubt"),
    ("prompt_clarification", "Prompt Clarification"),
    ("delegation_suggestion", "Delegation Suggestion"),
    ("identity_reflection", "Identity Reflection"),
    ("refocus", "Refocus Suggestion"),
    ("regeneration", "Plan Regeneration"),
]

MEMORY_MODES = [
    ("none", "None"),
    ("session", "Session"),
    ("long_term", "Long-Term"),
]

# Persona reasoning style
PERSONA_MODES = [
    ("default", "Default"),
    ("improviser", "Improviser"),
    ("planner", "Planner"),
    ("reflector", "Reflector"),
]

THINKING_STYLES = [
    ("cot", "Chain of Thought"),
    ("direct", "Direct Answer"),
    ("reflective", "Reflective"),
]

# Memory chain retrieval behavior
MEMORY_CHAIN_MODES = [
    ("automatic", "Automatic"),
    ("manual", "Manual"),
]

ROLE_CHOICES = [
    ("user", "User"),
    ("assistant", "Assistant"),
]

from assistants.constants import THOUGHT_CATEGORY_CHOICES

# Thought log modes
THOUGHT_MODES = [
    ("default", "Default"),
    ("dream", "Dream"),
]

COLLABORATION_STYLES = [
    ("harmonizer", "Harmonizer"),
    ("challenger", "Challenger"),
    ("strategist", "Strategist"),
    ("supporter", "Supporter"),
    ("autonomous", "Autonomous"),
]

CONFLICT_RESOLUTIONS = [
    ("pause_and_reflect", "Pause and Reflect"),
    ("delegate_to_mediator", "Delegate to Mediator"),
    ("suppress_and_continue", "Suppress and Continue"),
]

# Planning history event types
PLANNING_EVENT_TYPES = [
    ("objective_added", "Objective Added"),
    ("task_modified", "Task Modified"),
    ("milestone_completed", "Milestone Completed"),
    ("reflection_recorded", "Reflection Recorded"),
    ("plan_regenerated", "Plan Regenerated"),
]


# --- Models ---

from .assistant import *

