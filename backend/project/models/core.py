# project/models.py

import uuid
from django.db import models, IntegrityError
from django.conf import settings
from django.utils.text import slugify
from django.core.validators import MaxLengthValidator
from mcp_core.models import DevDoc  # at top


class ProjectType(models.TextChoices):
    GENERAL = "general", "General"
    ASSISTANT = "assistant", "Assistant"
    STORYBOOK = "storybook", "Storybook"
    GARDENING = "gardening", "Gardening"
    FARMING = "farming", "Farming"


class ProjectStatus(models.TextChoices):
    ACTIVE = "active", "Active"
    COMPLETED = "completed", "Completed"
    ON_HOLD = "on_hold", "On Hold"
    CANCELLED = "cancelled", "Cancelled"





class Project(models.Model):

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="projects"
    )
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True)
    theme = models.CharField(max_length=100, blank=True)
    image_style = models.CharField(max_length=100, blank=True)
    narrator_voice = models.CharField(
        max_length=100,
        blank=True,
        choices=[("Echo", "Echo"), ("Nova", "Nova")],
        validators=[MaxLengthValidator(100)],
    )
    is_public = models.BooleanField(default=False)
    participants = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="collaborative_projects",
        blank=True,
        through="ProjectParticipant",
    )
    team = models.ManyToManyField(
        "assistants.Assistant", related_name="team_projects", blank=True
    )
    team_chain = models.ForeignKey(
        "assistants.AssistantMemoryChain",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="team_projects",
    )

    # Project fields
    project_type = models.CharField(
        max_length=50, choices=ProjectType.choices, default=ProjectType.GENERAL
    )
    assistant = models.ForeignKey(
        "assistants.Assistant", null=True, blank=True, on_delete=models.SET_NULL
    )
    assistant_project = models.ForeignKey(
        "assistants.AssistantProject",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="linked_projects",
    )
    narrative_thread = models.ForeignKey(
        "mcp_core.NarrativeThread",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="narrative_projects",
    )
    thread = models.ForeignKey(
        "mcp_core.NarrativeThread",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="projects",
    )
    goal = models.TextField(blank=True, null=True)
    initial_prompt = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=50, choices=ProjectStatus.choices, default=ProjectStatus.ACTIVE
    )

    dev_docs = models.ManyToManyField(
        "mcp_core.DevDoc",
        blank=True,
        related_name="projects",
        help_text="Docs related to this project's goals or background context.",
    )
    created_from_memory = models.ForeignKey(
        "memory.MemoryEntry",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="spawned_projects",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]

    def _generate_unique_slug(self, base_slug: str) -> str:
        """Return a slug that is unique for the given base."""
        slug = base_slug
        counter = 1
        while Project.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        return slug

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)[:40]
            if not base_slug:
                base_slug = "project"
            self.slug = self._generate_unique_slug(base_slug)

        attempts = 0
        while True:
            try:
                super().save(*args, **kwargs)
                break
            except IntegrityError:
                attempts += 1
                if attempts > 5:
                    raise
                base_slug = slugify(self.title)[:40] or "project"
                self.slug = self._generate_unique_slug(base_slug)

    def __str__(self):
        return f"{self.title} ({self.project_type})"

    # Task helpers
    def get_open_tasks(self):
        """Return queryset of tasks not marked as done."""
        return self.core_tasks.exclude(status="done")

    def get_completed_tasks(self):
        """Return queryset of tasks marked as done."""
        return self.core_tasks.filter(status="done")

    def open_task_count(self):
        return self.get_open_tasks().count()

    def completed_task_count(self):
        return self.get_completed_tasks().count()

    def completion_percent(self):
        total = self.core_tasks.count()
        if total == 0:
            return 0
        return int((self.completed_task_count() / total) * 100)


class ProjectParticipant(models.Model):
    """Join table linking users to projects with a specific role."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="project_participations",
    )
    project = models.ForeignKey(
        "project.Project",
        on_delete=models.CASCADE,
        related_name="participant_links",
    )
    role = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "project")

    def __str__(self) -> str:
        return f"{self.user} -> {self.project} ({self.role})"




class ProjectMemoryLink(models.Model):
    """Links a project to a memory entry with an optional reason and
    timestamp."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        "project.Project", on_delete=models.CASCADE, related_name="linked_memories"
    )
    memory = models.ForeignKey("memory.MemoryEntry", on_delete=models.CASCADE)
    reason = models.TextField(blank=True, null=True)
    linked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["project", "memory"],
                name="unique_project_memory",
            )
        ]
        ordering = ["-linked_at"]

    def __str__(self):
        return f"{self.project} -> {self.memory}"

