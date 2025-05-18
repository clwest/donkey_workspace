from django.db import models
import uuid
from django.contrib.auth import get_user_model
from mcp_core.models import MemoryContext
from django.contrib.postgres.fields import ArrayField


User = get_user_model()

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
    preferred_llm = models.CharField(max_length=50, choices=LLM_CHOICES, default="gpt-4o")
    execution_mode = models.CharField(max_length=50, choices=EXECUTION_MODE_CHOICES, default="direct")

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
        return f"{self.name} ({self.preferred_llm}, {self.execution_style})"
    
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