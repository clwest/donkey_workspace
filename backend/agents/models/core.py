import uuid

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone
from mcp_core.models import MemoryContext, Tag
from pgvector.django import VectorField

User = settings.AUTH_USER_MODEL

LLM_CHOICES = [
    ("gpt-4o", "GPT-4o"),
    ("claude-3-opus", "Claude 3 Opus"),
    ("llama3", "LLaMA 3"),
    ("mistral", "Mistral"),
]

EXECUTION_MODE_CHOICES = [
    ("direct", "Direct Execution"),
    ("chain-of-thought", "Chain of Thought"),
    ("reflection", "Reflection Before Action"),
]


class Agent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    specialty = models.CharField(max_length=255, blank=True)
    AGENT_TYPE_CHOICES = [
        ("reflector", "Reflector"),
        ("reasoner", "Reasoner"),
        ("executor", "Executor"),
        ("general", "General"),
    ]
    agent_type = models.CharField(
        max_length=20,
        choices=AGENT_TYPE_CHOICES,
        default="general",
        help_text="Categorize the agent by its role in the assistant system.",
    )
    metadata = models.JSONField(default=dict, blank=True)
    tags = ArrayField(models.CharField(max_length=100), blank=True, default=list)
    skills = ArrayField(models.CharField(max_length=100), blank=True, default=list)
    trained_documents = models.ManyToManyField(
        "intel_core.Document",
        blank=True,
        related_name="trained_agents",
    )
    verified_skills = models.JSONField(
        default=list,
        blank=True,
        help_text=(
            "List of verified skills with metadata: "
            '[{"skill":"name", "source":"doc.pdf", "confidence":0.0, "last_verified":"ISO8601"}]'
        ),
    )
    strength_score = models.FloatField(default=0.0)
    readiness_score = models.FloatField(default=0.0)
    is_demo = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    reactivated_at = models.DateTimeField(null=True, blank=True)
    preferred_llm = models.CharField(
        max_length=50, choices=LLM_CHOICES, default="gpt-4o"
    )
    execution_mode = models.CharField(
        max_length=50, choices=EXECUTION_MODE_CHOICES, default="direct"
    )

    parent_assistant = models.ForeignKey(
        "assistants.Assistant",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_agents",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} ({self.preferred_llm}, {self.execution_mode})"


class AgentThought(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    agent = models.ForeignKey(
        "Agent", on_delete=models.CASCADE, related_name="thoughts"
    )
    input_text = models.TextField()
    response_text = models.TextField(blank=True, null=True)
    reasoning = models.TextField(blank=True, null=True)
    error_message = models.TextField(blank=True, null=True)
    tags = ArrayField(models.CharField(max_length=100), blank=True, default=list)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Thought from {self.agent.name} at {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}"


class AgentFeedbackLog(models.Model):
    agent = models.ForeignKey(
        "Agent", on_delete=models.CASCADE, related_name="feedback_logs"
    )
    task = models.ForeignKey(
        "assistants.AssistantNextAction",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    feedback_text = models.TextField()
    feedback_type = models.CharField(max_length=50, default="reflection")
    score = models.FloatField(null=True, blank=True)
    dissent_reason = models.TextField(blank=True)
    is_dissent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display only
        return f"Feedback for {self.agent.name} ({self.feedback_type})"


class AgentTrainingAssignment(models.Model):

    agent = models.ForeignKey(
        "Agent", on_delete=models.CASCADE, related_name="training_assignments"
    )
    document = models.ForeignKey(
        "intel_core.Document",
        on_delete=models.CASCADE,
        related_name="agent_training_assignments",
    )
    assistant = models.ForeignKey(
        "assistants.Assistant",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="agent_training_assignments",
    )
    completed = models.BooleanField(default=False)
    assigned_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-assigned_at"]

    def __str__(self):  # pragma: no cover - display only
        return f"Training for {self.agent.name} -> {self.document.title}"


class AgentSkill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    related_skills = models.ManyToManyField("self", symmetrical=False, blank=True)
    embedding = VectorField(dimensions=1536)


class AgentSkillLink(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    skill = models.ForeignKey(AgentSkill, on_delete=models.CASCADE)
    source = models.CharField(max_length=50, default="training")
    strength = models.FloatField(default=0.5)
    created_at = models.DateTimeField(auto_now_add=True)


class AgentCluster(models.Model):

    name = models.CharField(max_length=255)
    purpose = models.TextField(blank=True)
    project = models.ForeignKey(
        "assistants.AssistantProject",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="agent_clusters",
    )
    agents = models.ManyToManyField(Agent, related_name="clusters", blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class AgentReactivationVote(models.Model):
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    voter = models.ForeignKey(
        Agent,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="reactivation_votes",
    )
    reason = models.TextField()
    approved = models.BooleanField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)


class FarewellTemplate(models.Model):
    """Stores customizable farewell message templates."""

    name = models.CharField(max_length=100)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return self.name


class TrainedAgentLog(models.Model):
    """Record symbolic training sessions for agents before promotion."""

    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    label = models.CharField(max_length=150)
    document_set = models.ForeignKey(
        "intel_core.DocumentSet", on_delete=models.SET_NULL, null=True, blank=True
    )
    prompt = models.ForeignKey(
        "prompts.Prompt", on_delete=models.SET_NULL, null=True, blank=True
    )
    project = models.ForeignKey(
        "assistants.AssistantProject", on_delete=models.SET_NULL, null=True, blank=True
    )
    memory_entry = models.ForeignKey(
        "agents.SwarmMemoryEntry", on_delete=models.SET_NULL, null=True, blank=True
    )
    skill_matrix = models.JSONField(default=list, blank=True)
    document_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:  # pragma: no cover - display helper
        return self.label


class KnowledgeGrowthLog(models.Model):
    """Track knowledge uploads for an agent."""

    ORIGIN_CHOICES = [
        ("url", "URL"),
        ("pdf", "PDF"),
        ("manual", "Manual"),
    ]

    agent = models.ForeignKey(
        Agent, on_delete=models.CASCADE, related_name="knowledge_logs"
    )
    document = models.ForeignKey(
        "intel_core.Document",
        on_delete=models.CASCADE,
        related_name="knowledge_logs",
    )
    summary = models.TextField(blank=True)
    origin = models.CharField(max_length=20, choices=ORIGIN_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"Growth log for {self.agent.name} -> {self.document.title}"
