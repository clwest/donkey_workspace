from django.db import models
import uuid
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from agents.models import SwarmMemoryEntry
from mcp_core.models import MemoryContext
from django.contrib.postgres.fields import ArrayField

User = settings.AUTH_USER_MODEL


class MemoryEntry(models.Model):
    # 🔑 Identity & Timestamps
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # 🧠 Core Content
    event = models.TextField()
    emotion = models.CharField(max_length=50, blank=True, null=True)
    importance = models.IntegerField(default=5)
    full_transcript = models.TextField(blank=True, null=True)
    is_conversation = models.BooleanField(default=False)

    # 🏷️ Metadata
    tags = models.ManyToManyField("mcp_core.Tag", blank=True)
    session_id = models.CharField(max_length=100, blank=True, null=True)
    voice_clip = models.FileField(upload_to="memory_voices/", blank=True, null=True)

    summary = models.TextField(blank=True, null=True)
    title = models.CharField(max_length=200, blank=True, default="")
    document = models.ForeignKey(
        "intel_core.Document",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="memory_entries",
    )
    type = models.CharField(max_length=100, default="general")
    is_summary = models.BooleanField(default=False)
    memory_type = models.CharField(max_length=50, blank=True, default="")
    auto_tagged = models.BooleanField(default=False)
    is_bookmarked = models.BooleanField(default=False)
    bookmark_label = models.CharField(max_length=100, blank=True, null=True)

    symbolic_change = models.BooleanField(default=False)
    related_campaign = models.ForeignKey(
        "agents.StabilizationCampaign",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="memory_entries",
    )
    is_demo = models.BooleanField(default=False)
    anchor = models.ForeignKey(
        "memory.SymbolicMemoryAnchor",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="memories",
    )

    # 🔗 Relations (project, assistant, chat session)
    related_project = models.ForeignKey(
        "project.Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="memory_entries",
    )
    assistant = models.ForeignKey(
        "assistants.Assistant",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="memories",
    )
    chat_session = models.ForeignKey(
        "assistants.ChatSession", on_delete=models.SET_NULL, null=True, blank=True
    )

    linked_agents = models.ManyToManyField(
        "agents.Agent", blank=True, related_name="memory_entries"
    )

    # 🧬 Embeddings
    embeddings = GenericRelation("embeddings.Embedding")

    context = models.ForeignKey(
        "mcp_core.MemoryContext",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="memory_entries",
    )

    # Original narrative context thread for this memory
    narrative_thread = models.ForeignKey(
        "mcp_core.NarrativeThread",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="memories",
    )
    # Active discussion thread (may differ from narrative_thread)
    thread = models.ForeignKey(
        "mcp_core.NarrativeThread",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="thread_memories",
    )

    parent_memory = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="mutations",
    )

    # 🧑 Source Information
    source_role = models.CharField(
        max_length=50,
        choices=[
            ("user", "User"),
            ("assistant", "Assistant"),
            ("agent", "Agent"),
            ("system", "System"),
            ("external", "External"),
        ],
        default="assistant",
    )
    source_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="memory_entries",
    )

    linked_thought = models.ForeignKey(
        "assistants.AssistantThoughtLog",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="direct_linked_memories",
    )

    # 🧩 Polymorphic Link (replaces `linked_thought`)
    linked_content_type = models.ForeignKey(
        ContentType, on_delete=models.SET_NULL, null=True, blank=True
    )
    # CharField allows linking to objects with either UUID or integer primary keys
    linked_object_id = models.CharField(
        max_length=64,
        null=True,
        blank=True,
    )
    linked_object = GenericForeignKey("linked_content_type", "linked_object_id")
    tool_response = models.JSONField(null=True, blank=True)

    # 📈 Scoring & Context
    relevance_score = models.FloatField(default=0.0)
    context_tags = models.JSONField(default=list, blank=True)
    triggered_by = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.timestamp} - {self.event[:30]}..."

    def generate_memory_title(self):
        if self.title:
            return self.title
        if self.summary:
            return self.summary[:60]
        return self.event[:60]

    def save(self, *args, **kwargs):
        if not self.title:
            self.title = self.generate_memory_title()
        creating = self._state.adding
        super().save(*args, **kwargs)
        if not self.context:
            ctx = MemoryContext.objects.create(
                target_content_type=ContentType.objects.get_for_model(MemoryEntry),
                target_object_id=self.id,
                content=self.summary or self.event,
            )
            self.context = ctx
            super().save(update_fields=["context"])
        elif str(self.context.target_object_id or "") != str(self.id):
            self.context.target_object_id = str(self.id)
            self.context.save(update_fields=["target_object_id"])

    @property
    def source_name(self):
        if self.source_role == "user" and self.source_user:
            return self.source_user.name or self.source_user.username
        elif self.source_role == "assistant" and self.assistant:
            return self.assistant.name
        elif self.source_role == "agent" and hasattr(self.linked_object, "name"):
            return self.linked_object.name
        elif self.source_role == "system":
            return "System"
        elif self.source_role == "external":
            return "External Source"
        return "Unknown"

    def get_content_preview(self) -> str:
        """Return a short preview string for UI display."""
        content = self.event or self.summary or self.full_transcript
        if content:
            return content[:200]

        tags = list(self.tags.all()[:3])
        if tags:
            tag_str = ", ".join(f"#{t.slug}" for t in tags)
            return f"\U0001f9e0 Tags: {tag_str}"
        if self.session_id:
            # Use the actual emoji to ensure safe rendering in all terminals
            return f"🔄 Created by reflection for session {self.session_id}"
        return "(No content available)"

    @property
    def content_preview(self) -> str:
        return self.get_content_preview()


class MemoryChain(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    memories = models.ManyToManyField(MemoryEntry, related_name="chains")
    thread = models.ForeignKey(
        "mcp_core.NarrativeThread",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="chains",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    context_tags = models.JSONField(default=list, blank=True)
    task_type = models.CharField(max_length=100, blank=True, null=True)
    summary = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return self.title


class MemoryFeedback(models.Model):
    memory = models.ForeignKey(
        MemoryEntry, on_delete=models.CASCADE, related_name="feedback"
    )
    project = models.ForeignKey(
        "project.Project", null=True, blank=True, on_delete=models.SET_NULL
    )
    thought_log = models.ForeignKey(
        "assistants.AssistantThoughtLog",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    context_hint = models.TextField(blank=True)
    suggestion = models.TextField()
    explanation = models.TextField(blank=True)
    mutation_style = models.CharField(
        max_length=20,
        choices=[
            ("clarify", "Clarify"),
            ("shorten", "Shorten"),
            ("rephrase", "Rephrase"),
        ],
        null=True,
        blank=True,
    )
    submitted_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback on Memory {self.memory_id} by {self.submitted_by or 'anon'}"


# memory/models.py
class ReflectionFlag(models.Model):
    """Record a reflection flag on a memory entry with severity and reason."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    memory = models.ForeignKey(
        "memory.MemoryEntry", on_delete=models.CASCADE, related_name="flags"
    )
    reason = models.TextField()
    severity = models.CharField()


class SimulatedMemoryFork(models.Model):
    """Store hypothetical outcomes for alternate memory scenarios."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    original_memory = models.ForeignKey(
        MemoryEntry, on_delete=models.CASCADE, related_name="simulated_forks"
    )
    assistant = models.ForeignKey(
        "assistants.Assistant",
        on_delete=models.CASCADE,
        related_name="simulated_memory_forks",
    )
    simulated_outcome = models.TextField()
    hypothetical_action = models.TextField(blank=True, null=True)
    reason_for_simulation = models.TextField(blank=True)
    thought_log = models.ForeignKey(
        "assistants.AssistantThoughtLog",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="memory_forks",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Fork of {self.original_memory_id} by {self.assistant.name}"


class MemoryBranch(models.Model):
    """Branch speculative timeline from a SwarmMemoryEntry."""

    root_entry = models.ForeignKey(
        "agents.SwarmMemoryEntry",
        on_delete=models.CASCADE,
        related_name="branches",
    )
    fork_reason = models.TextField()
    speculative_outcome = models.TextField()
    approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Memory Branch"
        verbose_name_plural = "Memory Branches"
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"Branch of {self.root_entry_id}"


class SharedMemoryPool(models.Model):
    """Collection of shared key-value data accessible by multiple assistants."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    glossary_guidance = models.TextField(blank=True, default="")
    assistants = models.ManyToManyField(
        "assistants.Assistant", blank=True, related_name="shared_pools"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class SharedMemoryEntry(models.Model):
    """Key-value pair stored within a SharedMemoryPool."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    pool = models.ForeignKey(
        SharedMemoryPool, on_delete=models.CASCADE, related_name="entries"
    )
    key = models.CharField(max_length=255)
    value = models.JSONField(default=dict, blank=True)
    created_by = models.ForeignKey(
        "assistants.Assistant", on_delete=models.SET_NULL, null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("pool", "key")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.key}: {self.value}"


class BraidedMemoryStrand(models.Model):
    """Merge and align symbolic memories from alternate timelines."""

    primary_assistant = models.ForeignKey(
        "assistants.Assistant", on_delete=models.CASCADE, related_name="braided_strands"
    )
    alternate_sources = models.ManyToManyField(
        "agents.SwarmMemoryEntry", related_name="braided_into", blank=True
    )
    integration_notes = models.TextField(blank=True)
    symbolic_alignment_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class ContinuityAnchorPoint(models.Model):
    """Symbolic anchor ensuring identity coherence across timelines."""

    label = models.CharField(max_length=100)
    assistant = models.ForeignKey(
        "assistants.Assistant",
        on_delete=models.CASCADE,
        related_name="continuity_anchors",
    )
    anchor_memory = models.ForeignKey(
        "agents.SwarmMemoryEntry",
        on_delete=models.CASCADE,
        related_name="anchor_points",
    )
    mythic_tag = models.CharField(max_length=100)
    symbolic_signature = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return self.label


class SymbolicMemoryAnchor(models.Model):
    """Anchor term used for symbolic continuity across content."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(unique=True)
    label = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    glossary_guidance = models.TextField(blank=True, default="")
    is_focus_term = models.BooleanField(default=False)
    source = models.CharField(max_length=20, default="manual")
    created_from = models.CharField(max_length=20, default="manual")
    score_weight = models.FloatField(default=1.0)
    suggested_label = models.CharField(max_length=100, blank=True, null=True)
    mutation_status = models.CharField(
        max_length=20,
        choices=[
            ("pending", "pending"),
            ("applied", "applied"),
            ("rejected", "rejected"),
        ],
        default="pending",
    )
    mutation_source = models.CharField(max_length=64, blank=True, null=True)
    related_anchor = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="mutated_variants",
    )
    suggested_by = models.CharField(max_length=100, blank=True, null=True)
    assistant = models.ForeignKey(
        "assistants.Assistant",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="anchor_suggestions",
    )
    memory_context = models.ForeignKey(
        "mcp_core.MemoryContext",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="anchor_suggestions",
    )
    fallback_score = models.FloatField(null=True, blank=True)
    retrieved_from = models.CharField(max_length=100, blank=True, null=True)
    tags = models.ManyToManyField("mcp_core.Tag", blank=True)
    reinforced_by = models.ManyToManyField(
        "assistants.Assistant", blank=True, related_name="reinforced_anchors"
    )
    explanation = models.TextField(null=True, blank=True)
    protected = models.BooleanField(default=False)
    display_tooltip = models.BooleanField(default=False)
    display_location = models.JSONField(default=list, blank=True)
    acquisition_stage = models.CharField(
        max_length=20,
        choices=[
            ("unseen", "unseen"),
            ("exposed", "exposed"),
            ("acquired", "acquired"),
            ("reinforced", "reinforced"),
        ],
        default="unseen",
    )
    last_fallback = models.DateField(null=True, blank=True)
    last_used_in_reflection = models.DateTimeField(null=True, blank=True)
    total_uses = models.IntegerField(default=0)
    avg_score = models.FloatField(default=0.0)
    mutation_score_before = models.FloatField(null=True, blank=True)
    mutation_score_after = models.FloatField(null=True, blank=True)
    mutation_score_delta = models.FloatField(null=True, blank=True)
    is_stable = models.BooleanField(default=False)
    stabilized_at = models.DateTimeField(null=True, blank=True)
    drift_priority_score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["slug"]

    def __str__(self):
        return self.label

    def save(self, *args, **kwargs):
        if (
            self.mutation_score_before is not None
            and self.mutation_score_after is not None
        ):
            self.mutation_score_delta = (
                self.mutation_score_after - self.mutation_score_before
            )
        super().save(*args, **kwargs)


class MemoryEmbeddingFailureLog(models.Model):
    """Log failed embedding attempts for later analysis and retry."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document_set = models.ForeignKey(
        "intel_core.DocumentSet",
        on_delete=models.CASCADE,
        related_name="embedding_failures",
    )
    chunk_index = models.IntegerField()
    text = models.TextField(blank=True)
    error_message = models.TextField(blank=True)
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]


class MemoryEntropyAudit(models.Model):
    """Record entropy metrics for an assistant's memory chain."""

    chain = models.ForeignKey(
        "assistants.AssistantMemoryChain",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="entropy_audits",
    )
    entropy_score = models.FloatField()
    tags = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"Entropy {self.entropy_score}"


class MemoryMergeSuggestion(models.Model):
    """Suggest merging two memories to reduce symbolic drift."""

    entry_a = models.ForeignKey(
        MemoryEntry, on_delete=models.CASCADE, related_name="merge_a"
    )
    entry_b = models.ForeignKey(
        MemoryEntry, on_delete=models.CASCADE, related_name="merge_b"
    )
    merge_reason = models.TextField()
    suggested_by = models.ForeignKey(
        "assistants.Assistant", on_delete=models.SET_NULL, null=True, blank=True
    )
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"Merge {self.entry_a_id} & {self.entry_b_id}"


class GlossaryRetryLog(models.Model):
    """Record glossary retry attempts and their outcomes."""

    RETRY_TYPES = [
        ("standard", "standard"),
        ("escalated", "escalated"),
    ]

    anchor = models.ForeignKey(
        SymbolicMemoryAnchor, on_delete=models.SET_NULL, null=True, blank=True
    )
    anchor_slug = models.SlugField(blank=True, default="")
    question = models.TextField()
    first_response = models.TextField()
    retry_response = models.TextField(blank=True, null=True)
    glossary_chunk_ids = models.JSONField(default=list, blank=True)
    guidance_injected = models.BooleanField(default=False)
    retried = models.BooleanField(default=False)
    retry_type = models.CharField(
        max_length=20, choices=RETRY_TYPES, default="standard"
    )
    score_diff = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]


class AnchorConvergenceLog(models.Model):
    """Record when an assistant successfully answers using a glossary anchor."""

    anchor = models.ForeignKey(
        SymbolicMemoryAnchor,
        on_delete=models.CASCADE,
        related_name="convergence_logs",
    )
    assistant = models.ForeignKey(
        "assistants.Assistant",
        on_delete=models.CASCADE,
    )
    memory = models.ForeignKey(
        MemoryEntry,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    guidance_used = models.BooleanField(default=False)
    retried = models.BooleanField(default=False)
    final_score = models.FloatField()
    error_message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"{self.anchor.slug} -> {self.assistant.name}"


class AnchorReinforcementLog(models.Model):
    """Record when an anchor is reinforced in memory."""

    anchor = models.ForeignKey(
        SymbolicMemoryAnchor,
        on_delete=models.CASCADE,
        related_name="reinforcement_logs",
    )
    assistant = models.ForeignKey(
        "assistants.Assistant",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    memory = models.ForeignKey(
        MemoryEntry,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    reason = models.CharField(max_length=64)
    score = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"{self.anchor.slug} reinforced"


class RAGGroundingLog(models.Model):
    """Log RAG grounding results for debugging retrieval."""

    assistant = models.ForeignKey(
        "assistants.Assistant", on_delete=models.CASCADE, related_name="rag_logs"
    )
    query = models.TextField()
    used_chunk_ids = ArrayField(models.CharField(max_length=64), default=list)
    fallback_triggered = models.BooleanField(default=False)
    glossary_hits = ArrayField(
        models.CharField(max_length=64), default=list, blank=True
    )
    glossary_misses = ArrayField(
        models.CharField(max_length=64), default=list, blank=True
    )
    retrieval_score = models.FloatField(default=0.0)
    fallback_reason = models.CharField(max_length=100, blank=True, null=True)
    expected_anchor = models.SlugField(blank=True, default="")
    corrected_score = models.FloatField(null=True, blank=True)
    raw_score = models.FloatField(null=True, blank=True)
    adjusted_score = models.FloatField(null=True, blank=True)
    glossary_boost_applied = models.FloatField(default=0.0)
    boosted_from_reflection = models.BooleanField(default=False)
    reflection_boost_score = models.FloatField(default=0.0)
    glossary_boost_type = models.CharField(
        max_length=20,
        choices=[("chunk", "chunk"), ("reflection", "reflection"), ("both", "both")],
        default="chunk",
    )
    fallback_threshold_used = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"{self.assistant} | {self.query[:20]}"


class RAGPlaybackLog(models.Model):
    """Store raw chunk retrieval scores for a query."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assistant = models.ForeignKey(
        "assistants.Assistant", on_delete=models.CASCADE, related_name="rag_playbacks"
    )
    query = models.TextField()
    query_term = models.CharField(max_length=255, blank=True, default="")
    memory_context = models.ForeignKey(
        "mcp_core.MemoryContext", on_delete=models.SET_NULL, null=True, blank=True
    )
    chunks = models.JSONField()
    score_cutoff = models.FloatField(null=True, blank=True)
    fallback_reason = models.CharField(max_length=100, null=True, blank=True)

    class PlaybackType(models.TextChoices):
        REFLECTION = "reflection", "Reflection"
        REPLAY = "replay", "Replay"
        MANUAL = "manual", "Manual"

    playback_type = models.CharField(
        max_length=20,
        choices=PlaybackType.choices,
        default=PlaybackType.MANUAL,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"Playback for {self.assistant.slug}"


class GlossaryChangeEvent(models.Model):
    """Record manual boosts or adjustments to glossary terms."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    term = models.CharField(max_length=100)
    boost = models.FloatField(default=0.0)
    created_by = models.ForeignKey(
        User, null=True, blank=True, on_delete=models.SET_NULL
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"{self.term} boost {self.boost}"


class ReflectionReplayLog(models.Model):
    """Store results of replaying a reflection with updated glossary anchors."""

    original_reflection = models.ForeignKey(
        "assistants.AssistantReflectionLog",
        on_delete=models.CASCADE,
        related_name="replays",
    )
    assistant = models.ForeignKey("assistants.Assistant", on_delete=models.CASCADE)
    memory_entry = models.ForeignKey(
        "memory.MemoryEntry", null=True, blank=True, on_delete=models.SET_NULL
    )
    old_score = models.FloatField(default=0.0)
    new_score = models.FloatField(default=0.0)
    reflection_score = models.FloatField(default=0.0)
    changed_anchors = ArrayField(
        models.CharField(max_length=100), default=list, blank=True
    )
    replayed_summary = models.TextField(blank=True, default="")
    drift_reason = models.CharField(max_length=200, null=True, blank=True)
    rag_playback = models.ForeignKey(
        "memory.RAGPlaybackLog",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="replay_logs",
    )
    is_priority = models.BooleanField(default=False)

    class ReplayStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        ACCEPTED = "accepted", "Accepted"
        SKIPPED = "skipped", "Skipped"

    status = models.CharField(
        max_length=20,
        choices=ReplayStatus.choices,
        default=ReplayStatus.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):  # pragma: no cover - display helper
        return f"Replay of {self.original_reflection_id}"


class GlossaryKeeperLog(models.Model):
    """Log actions taken by the Glossary Keeper daemon."""

    anchor = models.ForeignKey(
        SymbolicMemoryAnchor,
        on_delete=models.CASCADE,
        related_name="keeper_logs",
    )
    assistant = models.ForeignKey(
        "assistants.Assistant",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    action_taken = models.CharField(max_length=64)
    score_before = models.FloatField(null=True, blank=True)
    score_after = models.FloatField(null=True, blank=True)
    notes = models.TextField(blank=True, default="")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):  # pragma: no cover - display helper
        return f"{self.anchor.slug} | {self.action_taken}"
