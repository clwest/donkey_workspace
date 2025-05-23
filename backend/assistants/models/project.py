import uuid
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.text import slugify
from django.conf import settings
from .core import PLANNING_EVENT_TYPES
from assistants.models.reflection import AssistantReflectionLog
from memory.models import MemoryEntry
from prompts.models import Prompt
from mcp_core.models import Tag

class AssistantProject(models.Model):
    """Project workspace tied to a single assistant."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assistant = models.ForeignKey(
        "Assistant", on_delete=models.CASCADE, related_name="projects"
    )
    title = models.CharField(max_length=255)
    goal = models.TextField(
        blank=True,
        default="",
        help_text="Main goal or objective for this assistant project.",
    )
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(  # ✅ NEW
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assistant_projects",
    )
    status = models.CharField(max_length=50, default="active")
    summary = models.TextField(blank=True, null=True)
    mood = models.CharField(max_length=20, blank=True, null=True)
    memory_shift_score = models.FloatField(default=0.0)
    documents = models.ManyToManyField("intel_core.Document", blank=True)
    agents = models.ManyToManyField("agents.Agent", blank=True, related_name="projects")

    shared_objectives = models.ManyToManyField(
        "assistants.AssistantObjective",
        blank=True,
        related_name="shared_in_projects",
    )

    slug = models.SlugField(max_length=255, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("assistant", "title")
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            self.slug = f"{base_slug}-{str(self.id)[:8]}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.assistant.name})"

    def regenerate_project_plan_from_memory(self, reason: str = "memory_shift"):
        """Regenerate objectives and tasks from recent memories."""
        from django.utils import timezone
        from datetime import timedelta
        from memory.models import MemoryEntry
        from assistants.helpers.logging_helper import log_assistant_thought
        from assistants.utils.memory_project_planner import (
            build_project_plan_from_memories,
        )

        # Get recent high-importance memories for this assistant
        memories = list(
            MemoryEntry.objects.filter(assistant=self.assistant).order_by(
                "-created_at"
            )[:5]
        )
        if not memories:
            return

        plan = build_project_plan_from_memories(memories, title=self.title)
        self.summary = "; ".join(plan.get("objectives", []))
        self.memory_shift_score = sum(m.importance for m in memories) / len(memories)
        self.save(update_fields=["summary", "memory_shift_score"])

        from assistants.models.assistant import safe_create_planning_log

        safe_create_planning_log(
            project=self,
            event_type="plan_regenerated",
            summary=f"Plan regenerated due to {reason}",
        )

        log = log_assistant_thought(
            self.assistant,
            f"Regenerated project plan due to {reason}",
            project=self,
            thought_type="planning",
        )
        log.event = "project_plan_revised"
        log.source_reason = reason
        log.save()

        AssistantReflectionLog.objects.create(
            project=self,
            title="Plan regenerated",
            summary=self.summary or "Plan updated",
            mood=self.mood,
            linked_memory=memories[0],
        )


class AssistantProjectRole(models.Model):
    """Assign assistants to projects with specific roles."""

    assistant = models.ForeignKey(
        "assistants.Assistant", on_delete=models.CASCADE, related_name="project_roles"
    )
    project = models.ForeignKey(
        "assistants.AssistantProject", on_delete=models.CASCADE, related_name="roles"
    )
    role_name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("assistant", "project")

    def __str__(self):
        return f"{self.assistant.name} as {self.role_name}"


class AssistantTask(models.Model):
    """Individual task within an assistant project."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        "assistants.AssistantProject", on_delete=models.CASCADE, related_name="tasks"
    )
    objective = models.ForeignKey(
        "assistants.AssistantObjective",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
    )
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=50, default="pending")
    notes = models.TextField(blank=True)
    priority = models.IntegerField(default=0)
    source_type = models.CharField(
        max_length=20,
        choices=[("thought", "Thought"), ("memory", "Memory"), ("custom", "Custom")],
        default="custom",
    )
    source_id = models.UUIDField(null=True, blank=True)
    proposed_by = models.ForeignKey(
        "assistants.Assistant",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tasks_proposed",
    )
    assigned_assistant = models.ForeignKey(
        "assistants.Assistant",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="tasks_assigned",
    )
    tone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        choices=[
            ("neutral", "Neutral"),
            ("encouraging", "Encouraging"),
            ("direct", "Direct"),
            ("playful", "Playful"),
            ("urgent", "Urgent"),
            ("curious", "Curious"),
            ("empathetic", "Empathetic"),
        ],
        help_text="Tone that should be used when performing this task",
    )
    generated_from_mood = models.CharField(max_length=20, null=True, blank=True)
    confirmed_by_user = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class AssistantObjective(models.Model):
    """Goal defined for an assistant project."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        "AssistantProject",  # ✅ This must be AssistantProject, not just Project
        on_delete=models.CASCADE,
        related_name="objectives",
    )
    assistant = models.ForeignKey(
        "Assistant", on_delete=models.CASCADE, related_name="objectives"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_completed = models.BooleanField(default=False)
    delegated_assistant = models.ForeignKey(
        "Assistant",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="delegated_objectives",
    )
    generated_from_reflection = models.ForeignKey(
        "assistants.AssistantReflectionLog",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="generated_objectives",
    )
    source_memory = models.ForeignKey(
        "memory.MemoryEntry",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="generated_objectives",
    )
    linked_event = models.ForeignKey(
        "story.NarrativeEvent",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="objectives",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class AssistantPromptLink(models.Model):
    """Associates a project with a specific prompt."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        "project.Project", on_delete=models.CASCADE, related_name="linked_prompts"
    )
    prompt = models.ForeignKey(Prompt, on_delete=models.CASCADE)
    reason = models.TextField(blank=True, null=True)
    linked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("project", "prompt")

    def __str__(self):
        return f"Prompt link for {self.project.title}: {self.prompt.title}"


class AssistantMemoryChain(models.Model):
    """Sequence of related memories and prompts for a project."""

    MODE_CHOICES = [
        ("automatic", "Automatic"),
        ("manual", "Manual"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        "project.Project", on_delete=models.CASCADE, related_name="memory_chains"
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default="manual")
    filter_tags = models.ManyToManyField(
        "mcp_core.Tag", blank=True, related_name="filtered_memory_chains"
    )
    exclude_types = models.JSONField(default=list, blank=True)
    memories = models.ManyToManyField(MemoryEntry, blank=True)
    prompts = models.ManyToManyField(Prompt, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    is_team_chain = models.BooleanField(default=False)
    team_members = models.ManyToManyField(
        "assistants.Assistant",
        blank=True,
        related_name="team_memory_chains",
    )
    linked_project = models.ForeignKey(
        "project.Project",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="team_memory_chains",
    )
    shared_tags = ArrayField(models.CharField(max_length=50), default=list, blank=True)
    VISIBILITY_CHOICES = [
        ("all", "All"),
        ("assigned_only", "Assigned Only"),
        ("owner_only", "Owner Only"),
    ]
    visibility_scope = models.CharField(
        max_length=20, choices=VISIBILITY_CHOICES, default="all"
    )


class AssistantNextAction(models.Model):
    """Next step derived from an AssistantObjective."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    objective = models.ForeignKey(
        AssistantObjective, on_delete=models.CASCADE, related_name="next_actions"
    )
    content = models.CharField(max_length=255)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    assigned_agent = (
        models.ForeignKey(
            "agents.Agent",
            on_delete=models.CASCADE,
            related_name="agents_assigned",
        ),
    )
    thread = (
        models.ForeignKey(
            "mcp_core.NarrativeThread",
            null=True,
            blank=True,
            on_delete=models.SET_NULL,
            related_name="next_actions",
        ),
    )

    linked_thread = (
        models.ForeignKey(
            "mcp_core.NarrativeThread",
            on_delete=models.CASCADE,
        ),
    )
    origin_thought = (
        models.ForeignKey(
            "assistants.AssistantThoughtLog",
            null=True,
            blank=True,
            on_delete=models.SET_NULL,
            related_name="next_actions",
        ),
    )

    importance_score = models.FloatField(default=0.5)


class ProjectPlanningLog(models.Model):
    """Chronological log of planning events for an assistant project."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        "assistants.AssistantProject",
        on_delete=models.CASCADE,
        related_name="planning_logs",
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    event_type = models.CharField(max_length=50, choices=PLANNING_EVENT_TYPES)
    summary = models.CharField(max_length=255)

    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    object_id = models.UUIDField(null=True, blank=True)
    related_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.event_type} @ {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
    